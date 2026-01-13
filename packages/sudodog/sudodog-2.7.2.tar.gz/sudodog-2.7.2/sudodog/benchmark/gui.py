#!/usr/bin/env python3
"""
SudoDog Benchmark GUI - Simple tkinter interface for Windows users
"""

import sys
import os
import threading
import webbrowser
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
except ImportError:
    print("tkinter is required for GUI mode. Please install it.")
    sys.exit(1)

from sudodog.scanner.scanner import scan_for_shadow_agents, DetectedAgent
from sudodog.benchmark.tester import AgentTester
from sudodog.benchmark.api import BenchmarkAPI
from sudodog.benchmark.main import analyze_locally, get_machine_id

VERSION = "2.5.1"


class BenchmarkGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"SudoDog Benchmark v{VERSION}")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Set icon if available
        try:
            if os.name == 'nt':
                self.root.iconbitmap(default='')
        except:
            pass

        # Configure style
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('Segoe UI', 10))
        self.style.configure('Score.TLabel', font=('Segoe UI', 24, 'bold'))
        self.style.configure('Grade.TLabel', font=('Segoe UI', 18, 'bold'))

        # Variables
        self.agents: List[DetectedAgent] = []
        self.selected_agent: Optional[DetectedAgent] = None
        self.is_running = False

        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text="SudoDog Benchmark", style='Title.TLabel').pack()
        ttk.Label(header_frame, text="Test and score your AI agents", style='Subtitle.TLabel').pack()

        # Scan section
        scan_frame = ttk.LabelFrame(main_frame, text="Step 1: Find Agents", padding="10")
        scan_frame.pack(fill=tk.X, pady=(0, 10))

        self.scan_btn = ttk.Button(scan_frame, text="Scan for AI Agents", command=self.scan_agents)
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.scan_status = ttk.Label(scan_frame, text="Click to scan for running AI agents")
        self.scan_status.pack(side=tk.LEFT)

        # Agent selection
        agent_frame = ttk.LabelFrame(main_frame, text="Step 2: Select Agent", padding="10")
        agent_frame.pack(fill=tk.X, pady=(0, 10))

        self.agent_listbox = tk.Listbox(agent_frame, height=4, font=('Consolas', 10))
        self.agent_listbox.pack(fill=tk.X, pady=(0, 5))
        self.agent_listbox.bind('<<ListboxSelect>>', self.on_agent_select)

        self.agent_info = ttk.Label(agent_frame, text="No agent selected")
        self.agent_info.pack(fill=tk.X)

        # Benchmark section
        bench_frame = ttk.LabelFrame(main_frame, text="Step 3: Run Benchmark", padding="10")
        bench_frame.pack(fill=tk.X, pady=(0, 10))

        btn_row = ttk.Frame(bench_frame)
        btn_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(btn_row, text="Duration:").pack(side=tk.LEFT, padx=(0, 5))
        self.duration_var = tk.StringVar(value="30")
        duration_spin = ttk.Spinbox(btn_row, from_=10, to=120, width=5, textvariable=self.duration_var)
        duration_spin.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(btn_row, text="seconds").pack(side=tk.LEFT, padx=(0, 20))

        self.run_btn = ttk.Button(btn_row, text="Run Benchmark", command=self.run_benchmark, state=tk.DISABLED)
        self.run_btn.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(bench_frame, mode='determinate', length=400)
        self.progress.pack(fill=tk.X, pady=(0, 5))

        self.progress_label = ttk.Label(bench_frame, text="")
        self.progress_label.pack(fill=tk.X)

        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        score_row = ttk.Frame(results_frame)
        score_row.pack(fill=tk.X, pady=(0, 10))

        self.score_label = ttk.Label(score_row, text="--", style='Score.TLabel')
        self.score_label.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Label(score_row, text="/ 100", font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=(0, 20))

        self.grade_label = ttk.Label(score_row, text="", style='Grade.TLabel')
        self.grade_label.pack(side=tk.LEFT)

        # Results text
        self.results_text = scrolledtext.ScrolledText(results_frame, height=8, font=('Consolas', 9))
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Links row
        links_row = ttk.Frame(results_frame)
        links_row.pack(fill=tk.X)

        self.report_btn = ttk.Button(links_row, text="View Full Report", command=self.open_report, state=tk.DISABLED)
        self.report_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.leaderboard_btn = ttk.Button(links_row, text="View Leaderboard", command=self.open_leaderboard)
        self.leaderboard_btn.pack(side=tk.LEFT)

        # Store report URL
        self.report_url = None

    def scan_agents(self):
        self.scan_btn.config(state=tk.DISABLED)
        self.scan_status.config(text="Scanning...")
        self.agent_listbox.delete(0, tk.END)
        self.root.update()

        def do_scan():
            try:
                self.agents = scan_for_shadow_agents(quiet=True)
                self.root.after(0, self.update_agent_list)
            except Exception as e:
                self.root.after(0, lambda: self.scan_status.config(text=f"Error: {e}"))
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))

        threading.Thread(target=do_scan, daemon=True).start()

    def update_agent_list(self):
        self.scan_btn.config(state=tk.NORMAL)

        if not self.agents:
            self.scan_status.config(text="No AI agents detected. Make sure your agent is running.")
            self.agent_info.config(text="Start your AI agent, then scan again.")
        else:
            self.scan_status.config(text=f"Found {len(self.agents)} agent(s)")
            for agent in self.agents:
                conf = int(agent.confidence * 100)
                self.agent_listbox.insert(tk.END, f"{agent.suspected_framework.upper()} (PID {agent.pid}) - {conf}% confidence")

            # Auto-select first agent
            if len(self.agents) == 1:
                self.agent_listbox.selection_set(0)
                self.on_agent_select(None)

    def on_agent_select(self, event):
        selection = self.agent_listbox.curselection()
        if selection:
            idx = selection[0]
            self.selected_agent = self.agents[idx]
            cmd = self.selected_agent.command_line[:60] + "..." if len(self.selected_agent.command_line) > 60 else self.selected_agent.command_line
            self.agent_info.config(text=f"Command: {cmd}")
            self.run_btn.config(state=tk.NORMAL)
        else:
            self.selected_agent = None
            self.agent_info.config(text="No agent selected")
            self.run_btn.config(state=tk.DISABLED)

    def run_benchmark(self):
        if not self.selected_agent or self.is_running:
            return

        self.is_running = True
        self.run_btn.config(state=tk.DISABLED)
        self.scan_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.results_text.delete(1.0, tk.END)
        self.score_label.config(text="--")
        self.grade_label.config(text="")
        self.report_btn.config(state=tk.DISABLED)

        duration = int(self.duration_var.get())

        def do_benchmark():
            try:
                tester = AgentTester(self.selected_agent)

                self.root.after(0, lambda: self.progress_label.config(text="Analyzing configuration..."))
                tester.analyze_config()

                self.root.after(0, lambda: self.progress_label.config(text="Monitoring agent behavior..."))

                for i in range(duration):
                    if not self.is_running:
                        return
                    tester.capture_metrics()
                    progress = ((i + 1) / duration) * 100
                    remaining = duration - i - 1
                    self.root.after(0, lambda p=progress, r=remaining: self.update_progress(p, r))
                    import time
                    time.sleep(1)

                self.root.after(0, lambda: self.progress_label.config(text="Collecting results..."))
                results = tester.get_results()

                self.root.after(0, lambda: self.progress_label.config(text="Submitting for analysis..."))

                api = BenchmarkAPI()
                machine_id = get_machine_id()

                try:
                    response = api.submit_benchmark(results, machine_id)
                except:
                    response = analyze_locally(results)

                self.root.after(0, lambda: self.show_results(response))

            except Exception as e:
                self.root.after(0, lambda: self.progress_label.config(text=f"Error: {e}"))
            finally:
                self.is_running = False
                self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))

        threading.Thread(target=do_benchmark, daemon=True).start()

    def update_progress(self, progress, remaining):
        self.progress['value'] = progress
        self.progress_label.config(text=f"Monitoring... {remaining}s remaining (interact with your agent now!)")

    def show_results(self, response):
        self.progress['value'] = 100
        self.progress_label.config(text="Complete!")

        score = response.get('score', 0)
        grade = response.get('grade', '?')

        self.score_label.config(text=str(score))
        self.grade_label.config(text=grade)

        # Color the grade
        grade_colors = {
            'A+': '#22c55e', 'A': '#22c55e',
            'B+': '#84cc16', 'B': '#84cc16',
            'C+': '#eab308', 'C': '#eab308',
            'D': '#f97316',
            'F': '#ef4444'
        }
        color = grade_colors.get(grade, '#888888')
        self.grade_label.config(foreground=color)

        # Show details
        self.results_text.delete(1.0, tk.END)

        summary = response.get('summary', {})
        good = summary.get('good', [])
        needs_work = summary.get('needs_work', [])

        if good:
            self.results_text.insert(tk.END, "What's working well:\n", 'good_header')
            for item in good:
                self.results_text.insert(tk.END, f"  + {item}\n", 'good')
            self.results_text.insert(tk.END, "\n")

        if needs_work:
            self.results_text.insert(tk.END, "Areas for improvement:\n", 'warn_header')
            for item in needs_work:
                self.results_text.insert(tk.END, f"  - {item}\n", 'warn')

        # Configure tags
        self.results_text.tag_config('good_header', foreground='#22c55e', font=('Consolas', 9, 'bold'))
        self.results_text.tag_config('good', foreground='#22c55e')
        self.results_text.tag_config('warn_header', foreground='#f97316', font=('Consolas', 9, 'bold'))
        self.results_text.tag_config('warn', foreground='#f97316')

        # Enable report button if URL available
        self.report_url = response.get('report_url')
        if self.report_url:
            self.report_btn.config(state=tk.NORMAL)

    def open_report(self):
        if self.report_url:
            webbrowser.open(self.report_url)

    def open_leaderboard(self):
        webbrowser.open("https://dashboard.sudodog.com/leaderboard")

    def run(self):
        self.root.mainloop()


def main():
    app = BenchmarkGUI()
    app.run()


if __name__ == "__main__":
    main()
