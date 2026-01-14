"""
Scratch3 Analyzer GUI - Graphical User Interface for analyzing Scratch 3.0 projects
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font
import threading
import queue
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import pandas as pd

from .core import Scratch3Analyzer

class Scratch3AnalyzerGUI:
    """Scratch3 Analyzer 图形用户界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Scratch3 Analyzer v1.1.0")
        self.root.geometry("900x700")
        
        # 设置图标（如果有）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.analyzer = Scratch3Analyzer()
        self.output_queue = queue.Queue()
        self.processing_thread = None
        self.stop_processing = False
        
        self.setup_styles()
        self.create_widgets()
        
        # 启动队列处理器
        self.root.after(100, self.process_queue)
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        
        # 主题
        style.theme_use('clam')
        
        # 自定义颜色
        self.bg_color = "#f0f0f0"
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#6b8cbc"
        self.accent_color = "#ff6b6b"
        
        # 配置样式
        style.configure("Title.TLabel", 
                       font=("Arial", 16, "bold"),
                       foreground=self.primary_color)
        
        style.configure("Header.TLabel",
                       font=("Arial", 10, "bold"))
        
        style.configure("Primary.TButton",
                       font=("Arial", 10, "bold"),
                       background=self.primary_color,
                       foreground="white")
        
        style.configure("Secondary.TButton",
                       font=("Arial", 10),
                       background=self.secondary_color,
                       foreground="white")
        
        style.configure("Accent.TButton",
                       font=("Arial", 10, "bold"),
                       background=self.accent_color,
                       foreground="white")
    
    def create_widgets(self):
        """创建所有界面组件"""
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, 
                               text="Scratch3 Analyzer",
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="分析模式", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        mode_frame.columnconfigure(1, weight=1)
        
        self.mode_var = tk.StringVar(value="single")
        
        single_radio = ttk.Radiobutton(mode_frame, 
                                      text="单个文件分析",
                                      variable=self.mode_var,
                                      value="single",
                                      command=self.on_mode_change)
        single_radio.grid(row=0, column=0, padx=(0, 20))
        
        batch_radio = ttk.Radiobutton(mode_frame,
                                     text="批量分析",
                                     variable=self.mode_var,
                                     value="batch",
                                     command=self.on_mode_change)
        batch_radio.grid(row=0, column=1, sticky=tk.W)
        
        # 文件选择
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        # 单个文件选择
        ttk.Label(file_frame, text="SB3文件:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(0, 5))
        
        browse_file_btn = ttk.Button(file_frame, 
                                    text="浏览...",
                                    command=self.browse_file,
                                    style="Secondary.TButton")
        browse_file_btn.grid(row=0, column=2, pady=(0, 5))
        
        # 批量文件选择
        ttk.Label(file_frame, text="目录:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.dir_entry = ttk.Entry(file_frame)
        self.dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(0, 5))
        
        browse_dir_btn = ttk.Button(file_frame,
                                   text="浏览...",
                                   command=self.browse_directory,
                                   style="Secondary.TButton")
        browse_dir_btn.grid(row=1, column=2, pady=(0, 5))
        
        # 递归选项（仅批量模式）
        self.recursive_var = tk.BooleanVar(value=False)
        self.recursive_check = ttk.Checkbutton(file_frame,
                                              text="递归搜索子目录",
                                              variable=self.recursive_var)
        self.recursive_check.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # 输出选项
        output_frame = ttk.LabelFrame(main_frame, text="输出选项", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.columnconfigure(1, weight=1)
        
        self.export_var = tk.BooleanVar(value=True)
        export_check = ttk.Checkbutton(output_frame,
                                      text="导出到Excel文件",
                                      variable=self.export_var,
                                      command=self.on_export_change)
        export_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(output_frame, text="输出路径:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.output_entry = ttk.Entry(output_frame)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(0, 5))
        
        browse_output_btn = ttk.Button(output_frame,
                                      text="浏览...",
                                      command=self.browse_output,
                                      style="Secondary.TButton")
        browse_output_btn.grid(row=1, column=2, pady=(0, 5))
        
        # 进度显示
        progress_frame = ttk.LabelFrame(main_frame, text="进度", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           mode='indeterminate',
                                           length=400)
        self.progress_bar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.progress_label = ttk.Label(progress_frame, text="准备就绪")
        self.progress_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # 结果展示
        results_frame = ttk.LabelFrame(main_frame, text="结果", padding="10")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 创建文本区域
        self.results_text = scrolledtext.ScrolledText(results_frame,
                                                     height=10,
                                                     wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(0, 10))
        
        analyze_btn = ttk.Button(button_frame,
                                text="开始分析",
                                command=self.start_analysis,
                                style="Primary.TButton",
                                width=15)
        analyze_btn.grid(row=0, column=0, padx=(0, 10))
        
        stop_btn = ttk.Button(button_frame,
                             text="停止",
                             command=self.stop_analysis,
                             style="Accent.TButton",
                             width=15)
        stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame,
                              text="清空结果",
                              command=self.clear_results,
                              style="Secondary.TButton",
                              width=15)
        clear_btn.grid(row=0, column=2, padx=(0, 10))
        
        exit_btn = ttk.Button(button_frame,
                             text="退出",
                             command=self.root.quit,
                             style="Secondary.TButton",
                             width=15)
        exit_btn.grid(row=0, column=3)
        
        # 初始化模式
        self.on_mode_change()
        self.on_export_change()
    
    def on_mode_change(self):
        """处理模式改变事件"""
        mode = self.mode_var.get()
        
        if mode == "single":
            self.file_entry.config(state="normal")
            self.dir_entry.config(state="disabled")
            self.recursive_check.config(state="disabled")
        else:  # batch
            self.file_entry.config(state="disabled")
            self.dir_entry.config(state="normal")
            self.recursive_check.config(state="normal")
        
        # 自动生成输出文件名
        self.auto_generate_output()
    
    def on_export_change(self):
        """处理导出选项改变事件"""
        if self.export_var.get():
            self.output_entry.config(state="normal")
        else:
            self.output_entry.config(state="disabled")
    
    def browse_file(self):
        """浏览单个文件"""
        file_path = filedialog.askopenfilename(
            title="选择 Scratch 3.0 项目文件",
            filetypes=[("Scratch 3.0 Files", "*.sb3"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.auto_generate_output()
    
    def browse_directory(self):
        """浏览目录"""
        dir_path = filedialog.askdirectory(title="选择包含 SB3 文件的目录")
        
        if dir_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)
            self.auto_generate_output()
    
    def browse_output(self):
        """浏览输出文件"""
        initial_file = self.output_entry.get() or "analysis_results.xlsx"
        file_path = filedialog.asksaveasfilename(
            title="保存分析结果",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            initialfile=os.path.basename(initial_file)
        )
        
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)
    
    def auto_generate_output(self):
        """自动生成输出文件名"""
        if not self.export_var.get():
            return
        
        mode = self.mode_var.get()
        current_output = self.output_entry.get()
        
        if current_output and os.path.exists(current_output):
            return  # 用户已经指定了输出文件，不自动更改
        
        if mode == "single":
            file_path = self.file_entry.get()
            if file_path and os.path.exists(file_path):
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                dir_name = os.path.dirname(file_path)
                output_path = os.path.join(dir_name, f"{base_name}_analysis.xlsx")
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, output_path)
        else:  # batch
            dir_path = self.dir_entry.get()
            if dir_path and os.path.exists(dir_path):
                dir_name = os.path.basename(dir_path.rstrip("/\\"))
                parent_dir = os.path.dirname(dir_path)
                output_path = os.path.join(parent_dir, f"{dir_name}_batch_analysis.xlsx")
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, output_path)
    
    def start_analysis(self):
        """开始分析"""
        mode = self.mode_var.get()
        
        if mode == "single":
            file_path = self.file_entry.get().strip()
            if not file_path:
                messagebox.showerror("错误", "请选择要分析的 SB3 文件")
                return
            if not os.path.exists(file_path):
                messagebox.showerror("错误", f"文件不存在: {file_path}")
                return
        else:  # batch
            dir_path = self.dir_entry.get().strip()
            if not dir_path:
                messagebox.showerror("错误", "请选择要分析的目录")
                return
            if not os.path.exists(dir_path):
                messagebox.showerror("错误", f"目录不存在: {dir_path}")
                return
        
        # 获取输出路径
        output_path = None
        if self.export_var.get():
            output_path = self.output_entry.get().strip()
            if not output_path:
                messagebox.showerror("错误", "请指定输出文件路径")
                return
        
        # 清空结果区域
        self.clear_results()
        
        # 禁用按钮，开始进度条
        self.set_ui_state(False)
        self.progress_bar.start(10)
        self.progress_label.config(text="正在分析...")
        
        # 在工作线程中运行分析
        self.stop_processing = False
        self.processing_thread = threading.Thread(
            target=self.run_analysis,
            args=(mode, file_path if mode == "single" else dir_path, output_path),
            daemon=True
        )
        self.processing_thread.start()
    
    def run_analysis(self, mode: str, path: str, output_path: Optional[str]):
        """运行分析（在线程中执行）"""
        try:
            if mode == "single":
                self.queue_message(f"分析文件: {os.path.basename(path)}")
                
                result = self.analyzer.analyze_file(path, output_path)
                
                if not self.stop_processing:
                    self.queue_message("\n" + "="*50)
                    self.queue_message("分析完成!")
                    self.queue_message("="*50)
                    self.queue_message(f"文件: {os.path.basename(path)}")
                    self.queue_message(f"角色数量: {result['complexity']['total_sprites']}")
                    self.queue_message(f"代码块总数: {result['complexity']['total_blocks']}")
                    self.queue_message(f"变量数量: {result['complexity']['total_variables']}")
                    self.queue_message(f"列表数量: {result['complexity']['total_lists']}")
                    self.queue_message(f"复杂度得分: {result['complexity']['complexity_score']}")
                    
                    if output_path:
                        self.queue_message(f"\n结果已导出到: {output_path}")
                    
                    self.queue_message("\n" + "="*50)
            
            else:  # batch
                self.queue_message(f"分析目录: {path}")
                
                # 查找文件
                sb3_files = []
                if self.recursive_var.get():
                    sb3_files = list(Path(path).rglob("*.sb3"))
                else:
                    sb3_files = list(Path(path).glob("*.sb3"))
                
                if not sb3_files:
                    self.queue_message(f"错误: 在目录中未找到 .sb3 文件")
                    return
                
                self.queue_message(f"找到 {len(sb3_files)} 个 .sb3 文件")
                
                all_results = []
                for i, sb3_file in enumerate(sb3_files):
                    if self.stop_processing:
                        break
                    
                    self.queue_message(f"\n正在分析 [{i+1}/{len(sb3_files)}]: {sb3_file.name}")
                    
                    try:
                        result = self.analyzer.analyze_file(str(sb3_file))
                        result['file_info']['filename'] = sb3_file.name
                        all_results.append(result)
                        
                        self.queue_message(f"  角色: {result['complexity']['total_sprites']}, " +
                                         f"代码块: {result['complexity']['total_blocks']}, " +
                                         f"复杂度: {result['complexity']['complexity_score']}")
                    except Exception as e:
                        self.queue_message(f"  错误: {str(e)}")
                        continue
                
                if not self.stop_processing and all_results and output_path:
                    # 导出批量结果
                    self.queue_message(f"\n正在导出批量分析结果到: {output_path}")
                    
                    try:
                        self.analyzer.exporter.export_multiple_to_excel(all_results, output_path)
                        self.queue_message("批量导出完成!")
                    except Exception as e:
                        self.queue_message(f"导出错误: {str(e)}")
                
                if not self.stop_processing:
                    self.queue_message("\n" + "="*50)
                    self.queue_message(f"批量分析完成!")
                    self.queue_message(f"成功分析: {len(all_results)}/{len(sb3_files)} 个文件")
                    
                    if output_path:
                        self.queue_message(f"结果已导出到: {output_path}")
                    
                    self.queue_message("="*50)
        
        except Exception as e:
            self.queue_message(f"分析过程中发生错误: {str(e)}")
        
        finally:
            # 发送完成信号
            self.output_queue.put("DONE")
    
    def stop_analysis(self):
        """停止分析"""
        self.stop_processing = True
        self.queue_message("\n正在停止分析...")
    
    def clear_results(self):
        """清空结果区域"""
        self.results_text.delete(1.0, tk.END)
    
    def set_ui_state(self, enabled: bool):
        """设置UI状态（启用/禁用）"""
        state = "normal" if enabled else "disabled"
        
        # 禁用/启用所有主要控件
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for widget in child.winfo_children():
                    if widget not in [self.results_text, self.progress_bar, self.progress_label]:
                        try:
                            widget.configure(state=state)
                        except:
                            pass
    
    def queue_message(self, message: str):
        """将消息放入队列（线程安全）"""
        self.output_queue.put(message)
    
    def process_queue(self):
        """处理消息队列（在主线程中执行）"""
        try:
            while True:
                message = self.output_queue.get_nowait()
                
                if message == "DONE":
                    self.analysis_complete()
                else:
                    # 在结果区域显示消息
                    self.results_text.insert(tk.END, message + "\n")
                    self.results_text.see(tk.END)
                    self.results_text.update()
        
        except queue.Empty:
            pass
        
        # 每100毫秒检查一次队列
        self.root.after(100, self.process_queue)
    
    def analysis_complete(self):
        """分析完成时的处理"""
        self.progress_bar.stop()
        self.progress_label.config(text="分析完成")
        self.set_ui_state(True)
        self.processing_thread = None
    
    def run(self):
        """运行GUI应用程序"""
        self.root.mainloop()