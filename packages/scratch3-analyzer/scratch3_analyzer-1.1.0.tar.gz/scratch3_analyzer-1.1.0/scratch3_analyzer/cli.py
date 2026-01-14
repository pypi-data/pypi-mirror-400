import argparse
import sys
import os
from pathlib import Path

# 检查是否在GUI模式下需要导入tkinter
def check_tkinter():
    try:
        import tkinter
        return True
    except ImportError:
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Scratch3 Analyzer - Analyze Scratch 3.0 (.sb3) project files"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a single .sb3 file")
    analyze_parser.add_argument("file", help="Path to .sb3 file")
    analyze_parser.add_argument("-o", "--output", help="Output Excel file path")
    analyze_parser.add_argument("--no-excel", action="store_true", 
                               help="Don't export to Excel")
    
    batch_parser = subparsers.add_parser("batch", help="Analyze all .sb3 files in a directory")
    batch_parser.add_argument("directory", help="Directory containing .sb3 files")
    batch_parser.add_argument("-o", "--output", help="Output Excel file path")
    batch_parser.add_argument("--recursive", "-r", action="store_true",
                            help="Recursively search for .sb3 files")
    
    parser.add_argument("--version", action="store_true", 
                       help="Show version information")
    
    parser.add_argument("--gui", action="store_true",
                       help="Launch graphical user interface")
    
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(f"scratch3_analyzer v{__version__}")
        return 0
    
    if args.gui:
        # 启动GUI
        if not check_tkinter():
            print("错误: 需要 tkinter 来运行 GUI 版本")
            print("请安装 tkinter 或使用命令行版本")
            return 1
        
        from .gui import Scratch3AnalyzerGUI
        try:
            app = Scratch3AnalyzerGUI()
            app.run()
            return 0
        except Exception as e:
            print(f"启动 GUI 时发生错误: {e}")
            return 1
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 命令行模式
    from .core import Scratch3Analyzer
    
    analyzer = Scratch3Analyzer()
    
    try:
        if args.command == "analyze":
            if not Path(args.file).exists():
                print(f"Error: File '{args.file}' not found")
                return 1
            
            output_excel = None if args.no_excel else args.output
            result = analyzer.analyze_file(args.file, output_excel)
            
            print("\n" + "="*50)
            print("PROJECT ANALYSIS SUMMARY")
            print("="*50)
            print(f"File: {args.file}")
            print(f"Total Sprites: {result['complexity']['total_sprites']}")
            print(f"Total Blocks: {result['complexity']['total_blocks']}")
            print(f"Total Variables: {result['complexity']['total_variables']}")
            print(f"Total Lists: {result['complexity']['total_lists']}")
            print(f"Complexity Score: {result['complexity']['complexity_score']}")
            
            if output_excel:
                print(f"\nDetailed results exported to: {output_excel}")
            
        elif args.command == "batch":
            if not Path(args.directory).exists():
                print(f"Error: Directory '{args.directory}' not found")
                return 1
            
            if args.recursive:
                sb3_files = list(Path(args.directory).rglob("*.sb3"))
            else:
                sb3_files = list(Path(args.directory).glob("*.sb3"))
            
            if not sb3_files:
                print(f"No .sb3 files found in {args.directory}")
                return 0
            
            print(f"Found {len(sb3_files)} .sb3 file(s)")
            
            results = analyzer.analyze_directory(args.directory, args.output)
            
            if args.output:
                print(f"\nBatch analysis exported to: {args.output}")
                
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())