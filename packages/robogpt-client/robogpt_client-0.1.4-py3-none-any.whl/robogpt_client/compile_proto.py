#!/usr/bin/env python3
"""
Compile robogpt.proto into Python gRPC stubs under ./build.

This uses grpc_tools.protoc programmatically so you don't need protoc installed
system-wide. The well-known types are resolved via grpc_tools' bundled includes.

Usage:
    python compile_proto.py                           # Compile all proto files
    python compile_proto.py --proto_select RobotControl  # Compile specific proto file
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path

try:
    from grpc_tools import protoc
    import pkg_resources
except Exception as e:
    print("Missing dependencies. Please install: grpcio grpcio-tools protobuf", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parent
PROTO_DIR = ROOT / "protos"
OUT_DIR = ROOT / "build"
PKG_INCLUDE = pkg_resources.resource_filename('grpc_tools', '_proto')


def compile_proto(proto_files: list[str]) -> int:
    """
    Compile the given proto files.

    Args:
        proto_files: List of proto file paths to compile

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not proto_files:
        print(f"No .proto files found to compile")
        return 1

    args = [
        'protoc',
        f'-I{PROTO_DIR}',
        f'-I{PKG_INCLUDE}',
        f'--python_out={OUT_DIR}',
        f'--grpc_python_out={OUT_DIR}',
    ] + proto_files

    print("Running protoc with:", " ".join(args))
    print(f"Compiling {len(proto_files)} proto file(s):")
    for pf in proto_files:
        print(f"  - {Path(pf).name}")

    result = protoc.main(args)

    if result == 0:
        print(f"\n✓ Successfully compiled proto files to {OUT_DIR}")
    else:
        print(f"\n✗ Failed to compile proto files")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Compile proto files into Python gRPC stubs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Compile all proto files
  %(prog)s --proto_select RobotControl  # Compile RobotControl.proto
  %(prog)s --proto_select RobogptVision # Compile RobogptVision.proto
        """
    )
    parser.add_argument(
        '--proto_select',
        type=str,
        help='Name of specific proto file to compile (without .proto extension)',
        default=None
    )

    args = parser.parse_args()

    if args.proto_select:
        # Compile specific proto file
        proto_name = args.proto_select
        if not proto_name.endswith('.proto'):
            proto_name += '.proto'

        proto_path = PROTO_DIR / proto_name

        if not proto_path.exists():
            print(f"Error: Proto file not found: {proto_path}", file=sys.stderr)
            print(f"\nAvailable proto files in {PROTO_DIR}:")
            for p in sorted(PROTO_DIR.glob('*.proto')):
                print(f"  - {p.name}")
            return 1

        print(f"Compiling selected proto: {proto_name}")
        proto_files = [str(proto_path)]
    else:
        # Compile all proto files
        print(f"Compiling all proto files from {PROTO_DIR}")
        proto_files = [str(p) for p in PROTO_DIR.rglob('*.proto')]

        if not proto_files:
            print(f"No .proto files found in {PROTO_DIR}")
            return 1

    return compile_proto(proto_files)


if __name__ == "__main__":
    sys.exit(main())
