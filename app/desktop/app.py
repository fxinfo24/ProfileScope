# SocialInsight: GUI Implementation
# A user-friendly interface for the Social Media Profile Analyzer

import sys
import os
import json
import threading
import datetime
from typing import Dict, List, Any, Optional, Tuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")  # Set the backend

# Import the analyzer core
# Import the analyzer core
from app.core.analyzer import SocialMediaAnalyzer
class AnalyzerApp(tk.Tk):
    """Main application window for SocialInsight"""
    
    def __init__(self):
        super().__init__()
        
        self.title("SocialInsight: Social Media Profile Analyzer")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Set app icon (if available)
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use a modern theme
        
        # Custom colors
        self.colors = {
            "primary": "#4a6fa5",
            "secondary": "#6c757d",
            "success": "#28a745",
            "danger": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8",
            "light": "#f8f9fa",
            "dark": "#343a40",
            "white": "#ffffff",
            "bg_light": "#f5f5f5"
        }
        
        # Configure styles
        self.style.configure("Primary.TButton", 
                            background=self.colors["primary"], 
                            foreground=self.colors["white"],
                            font=("Helvetica", 11, "bold"))
        
        self.style.configure("Secondary.TButton", 
                            background=self.colors["secondary"], 
                            foreground=self.colors["white"])
        
        self.style.configure("TitleLabel.TLabel", 
                            font=("Helvetica", 16, "bold"),
                            padding=10)
        
        self.style.configure("Header.TLabel", 
                            font=("Helvetica", 14, "bold"),
                            padding=5)
        
        self.style.configure("Subheader.TLabel", 
                            font=("Helvetica", 12, "bold"),
                            padding=5)
        
        # Initialize our analyzer in background
        self.analyzer = None
        self.analysis_results = None
        self.init_analyzer_thread = threading.Thread(target=self._init_analyzer)
        self.init_analyzer_thread.daemon = True
        self.init_analyzer_thread.start()
        
        # Create main UI
        self._create_menu()
        self._create_main_frame()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _init_analyzer(self):
        """Initialize the analyzer in background thread"""
        self.status_var.set("Initializing analyzer...")
        try:
            self.analyzer = SocialMediaAnalyzer()
            self.status_var.set("Ready")
        except Exception as e:
            self.status_var.set(f"Error initializing analyzer: {str(e)}")
            messagebox.showerror("Initialization Error", 
                               f"Failed to initialize analyzer: {str(e)}")
    
    def _create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Analysis", command=self._reset_analysis)
        file_menu.add_command(label="Open Results", command=self._load_results)
        file_menu.add_command(label="Save Results", command=self._save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Configuration", command=self._show_config)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self._show_docs)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
    
    def _create_main_frame(self):
        """Create the main application frame with tabs"""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Create tabs
        self.input_frame = ttk.Frame(self.notebook)
        self.results_frame = ttk.Frame(self.notebook)
        self.timeline_frame = ttk.Frame(self.notebook)
        self.traits_frame = ttk.Frame(self.notebook)
        self.writing_frame = ttk.Frame(self.notebook)
        self.authenticity_frame = ttk.Frame(self.notebook)
        self.predictions_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.input_frame, text="Profile Input")
        self.notebook.add(self.results_frame, text="Summary")
        self.notebook.add(self.timeline_frame, text="Timeline")
        self.notebook.add(self.traits_frame, text="Traits & Interests")
        self.notebook.add(self.writing_frame, text="Writing Style")
        self.notebook.add(self.authenticity_frame, text="Authenticity")
        self.notebook.add(self.predictions_frame, text="Predictions")
        
        # Setup input frame
        self._setup_input_frame()
        
        # Disable other tabs until analysis is done
        for i in range(1, self.notebook.index("end")):
            self.notebook.tab(i, state="disabled")
    
    def _setup_input_frame(self):
        """Set up the profile input tab"""
        # Title
        title_label = ttk.Label(self.input_frame, 
                              text="Analyze Social Media Profile",
                              style="TitleLabel.TLabel")
        title_label.pack(pady=20)
        
        # Input form
        input_form = ttk.Frame(self.input_frame, padding=20)
        input_form.pack(fill=tk.BOTH, expand=True, padx=50)
        
        # Platform selection
        platform_frame = ttk.Frame(input_form)
        platform_frame.pack(fill=tk.X, pady=10)
        
        platform_label = ttk.Label(platform_frame, text="Platform:", width=15, anchor=tk.W)
        platform_label.pack(side=tk.LEFT)
        
        self.platform_var = tk.StringVar()
        self.platform_var.set("twitter")
        
        platform_combo = ttk.Combobox(platform_frame, 
                                     textvariable=self.platform_var,
                                     state="readonly",
                                     values=["twitter", "facebook"])
        platform_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Profile ID input
        profile_frame = ttk.Frame(input_form)
        profile_frame.pack(fill=tk.X, pady=10)
        
        profile_label = ttk.Label(profile_frame, text="Profile ID:", width=15, anchor=tk.W)
        profile_label.pack(side=tk.LEFT)
        
        self.profile_var = tk.StringVar()
        profile_entry = ttk.Entry(profile_frame, textvariable=self.profile_var)
        profile_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Collection method frame
        method_frame = ttk.LabelFrame(input_form, text="Data Collection Method", padding=10)
        method_frame.pack(fill=tk.X, pady=10)
        
        self.collection_method = tk.StringVar()
        self.collection_method.set("api")
        
        api_radio = ttk.Radiobutton(method_frame, text="API Access (Recommended)", 
                                  variable=self.collection_method, value="api")
        api_radio.pack(anchor=tk.W, pady=5)
        
        web_radio = ttk.Radiobutton(method_frame, text="Web Scraping", 
                                  variable=self.collection_method, value="web")
        web_radio.pack(anchor=tk.W, pady=5)
        
        manual_radio = ttk.Radiobutton(method_frame, text="Manual Input", 
                                     variable=self.collection_method, value="manual")
        manual_radio.pack(anchor=tk.W, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(input_form, text="Analysis Options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        # Include sentiment analysis
        self.sentiment_var = tk.BooleanVar(value=True)
        sentiment_check = ttk.Checkbutton(options_frame, 
                                        text="Include sentiment analysis",
                                        variable=self.sentiment_var)
        sentiment_check.pack(anchor=tk.W, pady=5)
        
        # Include authenticty analysis
        self.authenticity_var = tk.BooleanVar(value=True)
        authenticity_check = ttk.Checkbutton(options_frame, 
                                          text="Include authenticity analysis",
                                          variable=self.authenticity_var)
        authenticity_check.pack(anchor=tk.W, pady=5)
        
        # Include predictions
        self.predictions_var = tk.BooleanVar(value=True)
        predictions_check = ttk.Checkbutton(options_frame, 
                                          text="Include predictions",
                                          variable=self.predictions_var)
        predictions_check.pack(anchor=tk.W, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(input_form)
        button_frame.pack(fill=tk.X, pady=20)
        
        analyze_button = ttk.Button(button_frame, 
                                  text="Start Analysis",
                                  style="Primary.TButton",
                                  command=self._start_analysis)
        analyze_button.pack(side=tk.RIGHT, padx=5)
        
        clear_button = ttk.Button(button_frame, 
                                text="Clear",
                                style="Secondary.TButton",
                                command=self._clear_form)
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Progress frame (initially hidden)
        self.progress_frame = ttk.Frame(self.input_frame)
        
        progress_label = ttk.Label(self.progress_frame, text="Analysis in progress...")
        progress_label.pack(pady=10)
        
        self.progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(self.progress_frame, 
                                      orient=tk.HORIZONTAL,
                                      length=400,
                                      mode='determinate',
                                      variable=self.progress_var)
        progress_bar.pack(pady=10, fill=tk.X, padx=50)
        
        self.progress_status_var = tk.StringVar()
        self.progress_status_var.set("Initializing...")
        progress_status = ttk.Label(self.progress_frame, 
                                  textvariable=self.progress_status_var)
        progress_status.pack(pady=10)
    
    def _setup_results_summary(self):
        """Set up the results summary tab"""
        # Clear existing widgets
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not self.analysis_results:
            label = ttk.Label(self.results_frame, text="No analysis results available")
            label.pack(pady=50)
            return
        
        # Create scrollable frame
        canvas = tk.Canvas(self.results_frame)
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Profile metadata
        metadata = self.analysis_results["metadata"]
        
        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        platform_icon = ttk.Label(header_frame, text="🔍")  # Platform icon
        platform_icon.config(font=("Arial", 24))
        platform_icon.pack(side=tk.LEFT, padx=10)
        
        title = ttk.Label(header_frame, 
                        text=f"Profile Analysis: {metadata['profile_id']}",
                        style="TitleLabel.TLabel")
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Metadata section
        meta_frame = ttk.LabelFrame(scrollable_frame, text="Analysis Information", padding=10)
        meta_frame.pack(fill=tk.X, padx=20, pady=10)
        
        meta_grid = ttk.Frame(meta_frame)
        meta_grid.pack(fill=tk.X, pady=5)
        
        # Meta details in grid
        labels = ["Platform", "Profile ID", "Analysis Date", "Version"]
        values = [
            metadata["platform"],
            metadata["profile_id"],
            datetime.datetime.fromisoformat(metadata["analysis_date"]).strftime("%Y-%m-%d %H:%M"),
            metadata["analyzer_version"]
        ]
        
        for i, (label, value) in enumerate(zip(labels, values)):
            lbl = ttk.Label(meta_grid, text=f"{label}:", width=15, anchor=tk.W)
            lbl.grid(row=i, column=0, sticky=tk.W, pady=2)
            
            val = ttk.Label(meta_grid, text=value)
            val.grid(row=i, column=1, sticky=tk.W, pady=2)
        
        # Key findings
        findings_frame = ttk.LabelFrame(scrollable_frame, text="Key Findings", padding=10)
        findings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Personality traits summary
        if "content_analysis" in self.analysis_results and "personality_traits" in self.analysis_results["content_analysis"]:
            traits = self.analysis_results["content_analysis"]["personality_traits"]
            top_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]
            
            traits_text = "Top personality traits: " + ", ".join([f"{trait.capitalize()} ({score:.0%})" for trait, score in top_traits])
            traits_label = ttk.Label(findings_frame, text=traits_text)
            traits_label.pack(anchor=tk.W, pady=5)
        
        # Interests summary
        if "content_analysis" in self.analysis_results and "interests" in self.analysis_results["content_analysis"]:
            interests = self.analysis_results["content_analysis"]["interests"]
            top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)[:3]
            
            interests_text = "Top interests: " + ", ".join([f"{interest.capitalize()} ({score:.0%})" for interest, score in top_interests])
            interests_label = ttk.Label(findings_frame, text=interests_text)
            interests_label.pack(anchor=tk.W, pady=5)
        
        # Authenticity 
        if "authenticity_analysis" in self.analysis_results and "overall_authenticity" in self.analysis_results["authenticity_analysis"]:
            auth = self.analysis_results["authenticity_analysis"]["overall_authenticity"]
            
            auth_text = f"Authenticity score: {auth['score']:.0%} (Confidence: {auth['confidence']:.0%})"
            auth_label = ttk.Label(findings_frame, text=auth_text)
            auth_label.pack(anchor=tk.W, pady=5)
            
            if auth["potential_issues"]:
                issues_text = "Potential issues: " + ", ".join(auth["potential_issues"])
                issues_label = ttk.Label(findings_frame, text=issues_text)
                issues_label.pack(anchor=tk.W, pady=5)
        
        # Timeline summary
        if "content_analysis" in self.analysis_results and "timeline" in self.analysis_results["content_analysis"]:
            timeline = self.analysis_results["content_analysis"]["timeline"]
            
            if timeline:
                earliest = min(timeline, key=lambda x: datetime.datetime.strptime(x["date"], "%Y-%m-%d"))
                latest = max(timeline, key=lambda x: datetime.datetime.strptime(x["date"], "%Y-%m-%d"))
                
                timeline_text = f"Activity period: {earliest['date']} to {latest['date']} ({len(timeline)} events)"
                timeline_label = ttk.Label(findings_frame, text=timeline_text)
                timeline_label.pack(anchor=tk.W, pady=5)
        
        # Main summary charts
        charts_frame = ttk.LabelFrame(scrollable_frame, text="Summary Visualizations", padding=10)
        charts_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create charts grid 
        charts_grid = ttk.Frame(charts_frame)
        charts_grid.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Personality radar chart
        if "content_analysis" in self.analysis_results and "personality_traits" in self.analysis_results["content_analysis"]:
            traits = self.analysis_results["content_analysis"]["personality_traits"]
            
            fig1 = plt.Figure(figsize=(5, 4), dpi=100)
            ax1 = fig1.add_subplot(111, polar=True)
            
            categories = list(traits.keys())
            values = list(traits.values())
            
            # Close the polygon by appending the first value to the end
            values.append(values[0])
            categories.append(categories[0])
            
            # Compute angle for each category
            angles = [n / float(len(categories)-1) * 2 * 3.14159 for n in range(len(categories))]
            angles += angles[:1]  # Close the loop
            
            ax1.plot(angles, values, linewidth=2, linestyle='solid')
            ax1.fill(angles, values, alpha=0.3)
            
            # Set category labels
            ax1.set_xticks(angles[:-1])
            ax1.set_xticklabels([c.capitalize() for c in categories[:-1]])
            
            ax1.set_title("Personality Traits")
            
            chart1 = FigureCanvasTkAgg(fig1, charts_grid)
            chart1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
        
        # Interests bar chart
        if "content_analysis" in self.analysis_results and "interests" in self.analysis_results["content_analysis"]:
            interests = self.analysis_results["content_analysis"]["interests"]
            
            fig2 = plt.Figure(figsize=(5, 4), dpi=100)
            ax2 = fig2.add_subplot(111)
            
            # Sort by value
            interests = dict(sorted(interests.items(), key=lambda x: x[1], reverse=True))
            
            categories = list(interests.keys())
            values = list(interests.values())
            
            # Limit to top 6
            if len(categories) > 6:
                categories = categories[:6]
                values = values[:6]
            
            ax2.barh([c.capitalize() for c in categories], values, color=self.colors["primary"])
            ax2.set_title("Top Interests")
            ax2.set_xlim(0, 1)
            
            chart2 = FigureCanvasTkAgg(fig2, charts_grid)
            chart2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)
        
        # Add sentiment trend if available
        if ("content_analysis" in self.analysis_results and 
            "sentiment_trends" in self.analysis_results["content_analysis"] and
            self.analysis_results["content_analysis"]["sentiment_trends"]):
            
            sentiment = self.analysis_results["content_analysis"]["sentiment_trends"]
            
            if "trend" in sentiment and sentiment["trend"]:
                fig3 = plt.Figure(figsize=(10, 4), dpi=100)
                ax3 = fig3.add_subplot(111)
                
                periods = [item["period"] for item in sentiment["trend"]]
                values = [item["average_sentiment"] for item in sentiment["trend"]]
                
                ax3.plot(periods, values, marker='o', linestyle='-', color=self.colors["info"])
                ax3.set_title("Sentiment Trend Over Time")
                ax3.set_ylim(-1, 1)
                ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
                
                # Rotate x labels if many periods
                if len(periods) > 6:
                    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
                
                fig3.tight_layout()
                
                chart3 = FigureCanvasTkAgg(fig3, charts_grid)
                chart3.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    
    def _setup_timeline_tab(self):
        """Set up the timeline visualization tab"""
        pass  # Timeline implementation will go here
    
    def _setup_traits_tab(self):
        """Set up the personality traits and interests tab"""
        pass  # Traits implementation will go here
    
    def _setup_writing_tab(self):
        """Set up the writing style analysis tab"""
        # Clear existing widgets
        for widget in self.writing_frame.winfo_children():
            widget.destroy()
            
        if not self.analysis_results or "content_analysis" not in self.analysis_results or "writing_style" not in self.analysis_results["content_analysis"]:
            label = ttk.Label(self.writing_frame, text="No writing style data available")
            label.pack(pady=50)
            return
        
        writing_style = self.analysis_results["content_analysis"]["writing_style"]
        
        # Main container
        main_frame = ttk.Frame(self.writing_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, 
                        text="Writing Style Analysis",
                        style="TitleLabel.TLabel")
        title.pack(pady=20)
        
        # Create two columns
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left column - General metrics
        metrics_frame = ttk.LabelFrame(columns_frame, text="Style Metrics", padding=10)
        metrics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Create a radar chart for key metrics
        if all(k in writing_style for k in ["complexity", "formality", "emotional_tone", "vocabulary_diversity"]):
            metrics_fig = plt.Figure(figsize=(5, 4), dpi=100)
            metrics_ax = metrics_fig.add_subplot(111, polar=True)
            
            metrics = {
                "Complexity": writing_style["complexity"],
                "Formality": writing_style["formality"],
                "Emotional Tone": writing_style["emotional_tone"],
                "Vocabulary": writing_style["vocabulary_diversity"]
            }
            
            categories = list(metrics.keys())
            values = list(metrics.values())
            
            # Close the polygon
            values.append(values[0])
            categories.append(categories[0])
            
            # Angles
            angles = [n / float(len(categories)-1) * 2 * 3.14159 for n in range(len(categories))]
            angles += angles[:1]
            
            metrics_ax.plot(angles, values, linewidth=2, linestyle='solid')
            metrics_ax.fill(angles, values, alpha=0.3)
            
            metrics_ax.set_xticks(angles[:-1])
            metrics_ax.set_xticklabels(categories[:-1])
            
            metrics_chart = FigureCanvasTkAgg(metrics_fig, metrics_frame)
            metrics_chart.get_tk_widget().pack(pady=10)
        
        # Style metrics details
        metrics_details = ttk.Frame(metrics_frame)
        metrics_details.pack(fill=tk.X, pady=10)
        
        # Key metrics
        metric_keys = [
            ("complexity", "Complexity"),
            ("formality", "Formality"),
            ("emotional_tone", "Emotional Tone"),
            ("vocabulary_diversity", "Vocabulary Diversity")
        ]
        
        for key, label in metric_keys:
            if key in writing_style:
                metric_frame = ttk.Frame(metrics_details)
                metric_frame.pack(fill=tk.X, pady=2)
                
                metric_label = ttk.Label(metric_frame, text=label, width=20, anchor=tk.W)
                metric_label.pack(side=tk.LEFT)
                
                metric_bar = ttk.Progressbar(metric_frame, value=int(writing_style[key]*100), length=100)
                metric_bar.pack(side=tk.LEFT, padx=5)
                
                metric_value = ttk.Label(metric_frame, text=f"{writing_style[key]:.0%}")
                metric_value.pack(side=tk.LEFT)
        
        # Other metrics as text
        other_metrics = ttk.Frame(metrics_details)
        other_metrics.pack(fill=tk.X, pady=10)
        
        if "average_sentence_length" in writing_style:
            sent_length = ttk.Label(other_metrics, 
                                  text=f"Average sentence length: {writing_style['average_sentence_length']:.1f} words")
            sent_length.pack(anchor=tk.W, pady=2)
        
        if "word_count" in writing_style:
            word_count = ttk.Label(other_metrics, 
                                 text=f"Total word count: {writing_style['word_count']}")
            word_count.pack(anchor=tk.W, pady=2)
        
        # Right column - Distinctive elements
        distinctive_frame = ttk.LabelFrame(columns_frame, text="Distinctive Elements", padding=10)
        distinctive_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Frequent words
        if "frequent_words" in writing_style and writing_style["frequent_words"]:
            freq_frame = ttk.Frame(distinctive_frame)
            freq_frame.pack(fill=tk.X, pady=10)
            
            freq_label = ttk.Label(freq_frame, text="Frequently Used Words:", style="Subheader.TLabel")
            freq_label.pack(anchor=tk.W)
            
            # Word cloud placeholder (in a real app, could use wordcloud module)
            freq_cloud = ttk.Frame(freq_frame, height=100, relief=tk.SUNKEN)
            freq_cloud.pack(fill=tk.X, pady=5)
            
            words_text = ", ".join(writing_style["frequent_words"])
            words_label = ttk.Label(freq_cloud, text=words_text, wraplength=350)
            words_label.pack(padx=10, pady=10)
        
        # Distinctive phrases
        if "distinctive_phrases" in writing_style and writing_style["distinctive_phrases"]:
            phrase_frame = ttk.Frame(distinctive_frame)
            phrase_frame.pack(fill=tk.X, pady=10)
            
            phrase_label = ttk.Label(phrase_frame, text="Distinctive Phrases:", style="Subheader.TLabel")
            phrase_label.pack(anchor=tk.W)
            
            phrase_list = ttk.Frame(phrase_frame)
            phrase_list.pack(fill=tk.X, pady=5)
            
            for i, phrase in enumerate(writing_style["distinctive_phrases"]):
                phrase_item = ttk.Label(phrase_list, text=f'"{phrase}"')
                phrase_item.pack(anchor=tk.W, pady=2)
        
        # Stylistic fingerprint
        if "stylistic_fingerprint" in writing_style:
            fingerprint_frame = ttk.LabelFrame(main_frame, text="Stylistic Fingerprint", padding=10)
            fingerprint_frame.pack(fill=tk.X, pady=20)
            
            fingerprint = writing_style["stylistic_fingerprint"]
            
            # Hash display with a copy button
            hash_frame = ttk.Frame(fingerprint_frame)
            hash_frame.pack(fill=tk.X, pady=10)
            
            hash_label = ttk.Label(hash_frame, text="Style Hash:", width=15, anchor=tk.W)
            hash_label.pack(side=tk.LEFT)
            
            hash_value = tk.Entry(hash_frame, width=40)
            hash_value.insert(0, fingerprint["hash"])
            hash_value.configure(state="readonly")
            hash_value.pack(side=tk.LEFT, padx=5)
            
            copy_button = ttk.Button(hash_frame, text="Copy",
                                   command=lambda: self.clipboard_clear() or self.clipboard_append(fingerprint["hash"]))
            copy_button.pack(side=tk.LEFT, padx=5)
            
            # Signature features
            if "signature_features" in fingerprint:
                sig_frame = ttk.Frame(fingerprint_frame)
                sig_frame.pack(fill=tk.X, pady=10)
                
                sig_label = ttk.Label(sig_frame, text="Signature Features:", width=15, anchor=tk.W)
                sig_label.pack(side=tk.LEFT, anchor=tk.N)
                
                features_frame = ttk.Frame(sig_frame)
                features_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                for feature in fingerprint["signature_features"]:
                    feature_label = ttk.Label(features_frame, text=f"• {feature}")
                    feature_label.pack(anchor=tk.W, pady=2)
    
    def _setup_authenticity_tab(self):
        """Set up the authenticity analysis tab"""
        # Clear existing widgets
        for widget in self.authenticity_frame.winfo_children():
            widget.destroy()
            
        if not self.analysis_results or "authenticity_analysis" not in self.analysis_results:
            label = ttk.Label(self.authenticity_frame, text="No authenticity analysis data available")
            label.pack(pady=50)
            return
        
        auth_analysis = self.analysis_results["authenticity_analysis"]
        
        # Main container
        main_frame = ttk.Frame(self.authenticity_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, 
                        text="Profile Authenticity Analysis",
                        style="TitleLabel.TLabel")
        title.pack(pady=20)
        
        # Overall authenticity score
        if "overall_authenticity" in auth_analysis:
            overall = auth_analysis["overall_authenticity"]
            
            overall_frame = ttk.Frame(main_frame)
            overall_frame.pack(fill=tk.X, pady=20)
            
            # Score gauge
            score = overall["score"]
            
            gauge_fig = plt.Figure(figsize=(4, 3), dpi=100)
            gauge_ax = gauge_fig.add_subplot(111)
            
            # Create a half-circle gauge
            gauge_ax.set_theta_offset(3*3.14159/2)
            gauge_ax.set_theta_direction(-1)
            
            # Plot the gauge background
            theta = np.linspace(0, 3.14159, 100)
            radius = 1.0
            
            # Background arc
            gauge_ax.plot(theta, [radius] * len(theta), color='lightgray', linewidth=15)
            
            # Calculate score position
            score_theta = score * 3.14159
            score_x = np.cos(score_theta)
            score_y = np.sin(score_theta)
            
            # Determine color based on score
            if score < 0.4:
                score_color = self.colors["danger"]
            elif score < 0.7:
                score_color = self.colors["warning"]
            else:
                score_color = self.colors["success"]
            
            # Score arc
            gauge_ax.plot(theta[:int(score * len(theta))], 
                       [radius] * int(score * len(theta)), 
                       color=score_color, 
                       linewidth=15)
            
            # Add labels
            gauge_ax.text(-0.95, 0.15, "Fake", ha='center', va='center', fontsize=12)
            gauge_ax.text(0, 0.15, "Uncertain", ha='center', va='center', fontsize=12)
            gauge_ax.text(0.95, 0.15, "Authentic", ha='center', va='center', fontsize=12)
            
            # Add score in center
            gauge_ax.text(0, -0.2, f"Score: {score:.0%}", ha='center', va='center', 
                       fontsize=14, fontweight='bold')
            
            # Clean up the plot
            gauge_ax.set_ylim(0, 1.2)
            gauge_ax.set_xlim(-1.2, 1.2)
            gauge_ax.set_axis_off()
            
            gauge_canvas = FigureCanvasTkAgg(gauge_fig, overall_frame)
            gauge_canvas.get_tk_widget().pack()
            
            # Information below gauge
            info_frame = ttk.Frame(overall_frame)
            info_frame.pack(fill=tk.X, pady=10)
            
            confidence_label = ttk.Label(info_frame, 
                                       text=f"Analysis Confidence: {overall['confidence']:.0%}")
            confidence_label.pack(anchor=tk.CENTER)
            
            if "potential_issues" in overall and overall["potential_issues"]:
                issues_text = "Potential issues detected: " + ", ".join(overall["potential_issues"])
                issues_label = ttk.Label(info_frame, text=issues_text, foreground=self.colors["danger"])
                issues_label.pack(anchor=tk.CENTER, pady=5)
        
        # Create two-column layout for detailed analysis
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left column - Consistency & Bot analysis
        left_frame = ttk.Frame(columns_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Consistency score
        if "consistency_score" in auth_analysis:
            consistency_frame = ttk.LabelFrame(left_frame, text="Temporal Consistency", padding=10)
            consistency_frame.pack(fill=tk.X, pady=10)
            
            score = auth_analysis["consistency_score"]
            
            cons_label = ttk.Label(consistency_frame, text=f"Consistency Score: {score:.0%}")
            cons_label.pack(anchor=tk.W, pady=5)
            
            cons_bar = ttk.Progressbar(consistency_frame, value=int(score*100), length=200)
            cons_bar.pack(anchor=tk.W, pady=5)
            
            # Description based on score
            if score < 0.3:
                desc = "Very inconsistent activity patterns detected"
            elif score < 0.6:
                desc = "Some inconsistencies in activity patterns"
            else:
                desc = "Activity patterns appear consistent"
                
            cons_desc = ttk.Label(consistency_frame, text=desc)
            cons_desc.pack(anchor=tk.W, pady=5)
        
        # Bot likelihood analysis
        if "bot_likelihood" in auth_analysis:
            bot_frame = ttk.LabelFrame(left_frame, text="Bot Analysis", padding=10)
            bot_frame.pack(fill=tk.X, pady=10)
            
            bot = auth_analysis["bot_likelihood"]
            
            bot_label = ttk.Label(bot_frame, text=f"Bot Likelihood: {bot['score']:.0%}")
            bot_label.pack(anchor=tk.W, pady=5)
            
            bot_bar = ttk.Progressbar(bot_frame, value=int(bot['score']*100), length=200)
            bot_bar.pack(anchor=tk.W, pady=5)
            
            conf_label = ttk.Label(bot_frame, text=f"Analysis Confidence: {bot['confidence']:.0%}")
            conf_label.pack(anchor=tk.W, pady=5)
            
            # Indicator details if available
            if "indicators" in bot:
                indicators = bot["indicators"]
                
                ind_frame = ttk.Frame(bot_frame)
                ind_frame.pack(fill=tk.X, pady=5)
                
                ind_label = ttk.Label(ind_frame, text="Individual Indicators:")
                ind_label.pack(anchor=tk.W)
                
                for name, value in indicators.items():
                    ind_item = ttk.Frame(ind_frame)
                    ind_item.pack(fill=tk.X, pady=2)
                    
                    item_name = ttk.Label(ind_item, 
                                        text=name.replace("_", " ").capitalize(), 
                                        width=20,
                                        anchor=tk.W)
                    item_name.pack(side=tk.LEFT)
                    
                    item_bar = ttk.Progressbar(ind_item, value=int(value*100), length=100)
                    item_bar.pack(side=tk.LEFT, padx=5)
                    
                    item_value = ttk.Label(ind_item, text=f"{value:.0%}")
                    item_value.pack(side=tk.LEFT)
        
        # Right column - Activity patterns and style comparison
        right_frame = ttk.Frame(columns_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Activity pattern analysis
        if "activity_patterns" in auth_analysis:
            activity_frame = ttk.LabelFrame(right_frame, text="Activity Pattern Analysis", padding=10)
            activity_frame.pack(fill=tk.X, pady=10)
            
            patterns = auth_analysis["activity_patterns"]
            
            # Check if we have posting times distribution
            if "posting_times" in patterns and "distribution" in patterns["posting_times"]:
                dist = patterns["posting_times"]["distribution"]
                
                # Create a pie chart
                pie_fig = plt.Figure(figsize=(4, 3), dpi=100)
                pie_ax = pie_fig.add_subplot(111)
                
                labels = [k.capitalize() for k in dist.keys()]
                values = list(dist.values())
                
                pie_ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                pie_ax.set_title("Posting Time Distribution")
                
                pie_canvas = FigureCanvasTkAgg(pie_fig, activity_frame)
                pie_canvas.get_tk_widget().pack(pady=10)
                
                # Consistency value if available
                if "consistency" in patterns["posting_times"]:
                    cons = patterns["posting_times"]["consistency"]
                    cons_label = ttk.Label(activity_frame, 
                                        text=f"Posting time consistency: {cons:.0%}")
                    cons_label.pack(anchor=tk.W, pady=5)
            
            # Irregular patterns
            if "irregular_patterns" in patterns:
                irreg_text = "Irregular activity patterns detected" if patterns["irregular_patterns"] else "No irregular patterns detected"
                irreg_label = ttk.Label(activity_frame, text=irreg_text)
                irreg_label.pack(anchor=tk.W, pady=5)
            
            # Burst activities if any
            if "burst_activities" in patterns and patterns["burst_activities"]:
                burst_text = "Burst activities detected: " + ", ".join(patterns["burst_activities"])
                burst_label = ttk.Label(activity_frame, text=burst_text)
                burst_label.pack(anchor=tk.W, pady=5)
            
            # Dormant periods if any
            if "dormant_periods" in patterns and patterns["dormant_periods"]:
                dormant_text = "Dormant periods detected: " + ", ".join(patterns["dormant_periods"])
                dormant_label = ttk.Label(activity_frame, text=dormant_text)
                dormant_label.pack(anchor=tk.W, pady=5)
        
        # Style comparison
        if "style_comparison" in auth_analysis:
            style_frame = ttk.LabelFrame(right_frame, text="Writing Style Comparison", padding=10)
            style_frame.pack(fill=tk.X, pady=10)
            
            comparison = auth_analysis["style_comparison"]
            
            # Highest match information if available
            if "highest_match" in comparison and comparison["highest_match"]:
                highest = comparison["highest_match"]
                
                match_frame = ttk.Frame(style_frame)
                match_frame.pack(fill=tk.X, pady=10)
                
                match_label = ttk.Label(match_frame, text="Highest Style Match:", style="Subheader.TLabel")
                match_label.pack(anchor=tk.W)
                
                profile_name = ttk.Label(match_frame, 
                                      text=f"Profile: {highest['reference_profile']}")
                profile_name.pack(anchor=tk.W, pady=2)
                
                similarity = ttk.Label(match_frame, 
                                    text=f"Similarity: {highest['similarity_score']:.0%} (Confidence: {highest['confidence']:.0%})")
                similarity.pack(anchor=tk.W, pady=2)
                
                if "matching_features" in highest and highest["matching_features"]:
                    features_text = "Matching features: " + ", ".join(highest["matching_features"])
                    features_label = ttk.Label(match_frame, text=features_text)
                    features_label.pack(anchor=tk.W, pady=2)
            
            # All matches if available
            if "matches" in comparison and len(comparison["matches"]) > 1:
                all_matches_frame = ttk.Frame(style_frame)
                all_matches_frame.pack(fill=tk.X, pady=10)
                
                matches_label = ttk.Label(all_matches_frame, text="All Style Comparisons:", style="Subheader.TLabel")
                matches_label.pack(anchor=tk.W)
                
                # Sort by similarity score
                sorted_matches = sorted(comparison["matches"], 
                                      key=lambda x: x["similarity_score"], 
                                      reverse=True)
                
                for match in sorted_matches:
                    match_item = ttk.Frame(all_matches_frame)
                    match_item.pack(fill=tk.X, pady=2)
                    
                    item_name = ttk.Label(match_item, 
                                        text=match["reference_profile"], 
                                        width=20,
                                        anchor=tk.W)
                    item_name.pack(side=tk.LEFT)
                    
                    item_bar = ttk.Progressbar(match_item, 
                                             value=int(match["similarity_score"]*100), 
                                             length=100)
                    item_bar.pack(side=tk.LEFT, padx=5)
                    
                    item_value = ttk.Label(match_item, text=f"{match['similarity_score']:.0%}")
                    item_value.pack(side=tk.LEFT)
    
    def _setup_predictions_tab(self):
        """Set up the predictions tab"""
        # Clear existing widgets
        for widget in self.predictions_frame.winfo_children():
            widget.destroy()
            
        if not self.analysis_results or "predictions" not in self.analysis_results:
            label = ttk.Label(self.predictions_frame, text="No predictions data available")
            label.pack(pady=50)
            return
        
        predictions = self.analysis_results["predictions"]
        
        # Main container with scrolling
        pred_canvas = tk.Canvas(self.predictions_frame)
        pred_scrollbar = ttk.Scrollbar(self.predictions_frame, orient="vertical", 
                                     command=pred_canvas.yview)
        scrollable_pred = ttk.Frame(pred_canvas)
        
        scrollable_pred.bind(
            "<Configure>",
            lambda e: pred_canvas.configure(scrollregion=pred_canvas.bbox("all"))
        )
        
        pred_canvas.create_window((0, 0), window=scrollable_pred, anchor="nw")
        pred_canvas.configure(yscrollcommand=pred_scrollbar.set)
        
        pred_canvas.pack(side="left", fill="both", expand=True)
        pred_scrollbar.pack(side="right", fill="y")
        
        # Title and disclaimer
        title = ttk.Label(scrollable_pred, 
                        text="Predictions & Forecasts",
                        style="TitleLabel.TLabel")
        title.pack(pady=20)
        
        if "disclaimer" in predictions:
            disclaimer_frame = ttk.Frame(scrollable_pred, padding=10)
            disclaimer_frame.pack(fill=tk.X, padx=20)
            
            disclaimer_text = ttk.Label(disclaimer_frame, 
                                     text=predictions["disclaimer"],
                                     wraplength=600,
                                     foreground=self.colors["secondary"])
            disclaimer_text.pack()
        
        # Create a two-column layout for predictions
        columns_frame = ttk.Frame(scrollable_pred, padding=20)
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column
        left_frame = ttk.Frame(columns_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Future interests
        if "future_interests" in predictions and predictions["future_interests"]:
            interests_frame = ttk.LabelFrame(left_frame, text="Predicted Future Interests", padding=10)
            interests_frame.pack(fill=tk.X, pady=10)
            
            for interest in predictions["future_interests"]:
                interest_frame = ttk.Frame(interests_frame)
                interest_frame.pack(fill=tk.X, pady=5)
                
                interest_label = ttk.Label(interest_frame, 
                                        text=interest["interest"],
                                        font=("Helvetica", 11, "bold"))
                interest_label.pack(anchor=tk.W)
                
                conf_frame = ttk.Frame(interest_frame)
                conf_frame.pack(fill=tk.X, pady=2)
                
                conf_label = ttk.Label(conf_frame, text="Confidence: ", width=12, anchor=tk.W)
                conf_label.pack(side=tk.LEFT)
                
                conf_bar = ttk.Progressbar(conf_frame, 
                                        value=int(interest["confidence"]*100), 
                                        length=100)
                conf_bar.pack(side=tk.LEFT, padx=5)
                
                conf_value = ttk.Label(conf_frame, text=f"{interest['confidence']:.0%}")
                conf_value.pack(side=tk.LEFT)
                
                if "reasoning" in interest:
                    reason_label = ttk.Label(interest_frame, 
                                          text=f"Reasoning: {interest['reasoning']}",
                                          wraplength=350)
                    reason_label.pack(anchor=tk.W, pady=2)
        
        # Predicted behaviors
        if "potential_behaviors" in predictions and predictions["potential_behaviors"]:
            behaviors_frame = ttk.LabelFrame(left_frame, text="Predicted Behaviors", padding=10)
            behaviors_frame.pack(fill=tk.X, pady=10)
            
            for behavior in predictions["potential_behaviors"]:
                behavior_frame = ttk.Frame(behaviors_frame)
                behavior_frame.pack(fill=tk.X, pady=5)
                
                behavior_label = ttk.Label(behavior_frame, 
                                        text=behavior["behavior"],
                                        font=("Helvetica", 11, "bold"))
                behavior_label.pack(anchor=tk.W)
                
                conf_frame = ttk.Frame(behavior_frame)
                conf_frame.pack(fill=tk.X, pady=2)
                
                conf_label = ttk.Label(conf_frame, text="Confidence: ", width=12, anchor=tk.W)
                conf_label.pack(side=tk.LEFT)
                
                conf_bar = ttk.Progressbar(conf_frame, 
                                        value=int(behavior["confidence"]*100), 
                                        length=100)
                conf_bar.pack(side=tk.LEFT, padx=5)
                
                conf_value = ttk.Label(conf_frame, text=f"{behavior['confidence']:.0%}")
                conf_value.pack(side=tk.LEFT)
                
                if "reasoning" in behavior:
                    reason_label = ttk.Label(behavior_frame, 
                                          text=f"Reasoning: {behavior['reasoning']}",
                                          wraplength=350)
                    reason_label.pack(anchor=tk.W, pady=2)
        
        # Right column
        right_frame = ttk.Frame(columns_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Demographic predictions
        if "demographic_predictions" in predictions:
            demographics_frame = ttk.LabelFrame(right_frame, text="Demographic Predictions", padding=10)
            demographics_frame.pack(fill=tk.X, pady=10)
            
            demog = predictions["demographic_predictions"]
            
            # Age range
            if "age_range" in demog:
                age_frame = ttk.Frame(demographics_frame)
                age_frame.pack(fill=tk.X, pady=5)
                
                age_label = ttk.Label(age_frame, text="Age Range:", width=15, anchor=tk.W)
                age_label.pack(side=tk.LEFT)
                
                age_value = ttk.Label(age_frame, 
                                   text=f"{demog['age_range']['prediction']} (Confidence: {demog['age_range']['confidence']:.0%})")
                age_value.pack(side=tk.LEFT)
            
            # Education level
            if "education_level" in demog:
                edu_frame = ttk.Frame(demographics_frame)
                edu_frame.pack(fill=tk.X, pady=5)
                
                edu_label = ttk.Label(edu_frame, text="Education Level:", width=15, anchor=tk.W)
                edu_label.pack(side=tk.LEFT)
                
                edu_value = ttk.Label(edu_frame, 
                                   text=f"{demog['education_level']['prediction']} (Confidence: {demog['education_level']['confidence']:.0%})")
                edu_value.pack(side=tk.LEFT)
            
            # Occupation category
            if "occupation_category" in demog:
                occ_frame = ttk.Frame(demographics_frame)
                occ_frame.pack(fill=tk.X, pady=5)
                
                occ_label = ttk.Label(occ_frame, text="Occupation:", width=15, anchor=tk.W)
                occ_label.pack(side=tk.LEFT)
                
                occ_value = ttk.Label(occ_frame, 
                                   text=f"{demog['occupation_category']['prediction']} (Confidence: {demog['occupation_category']['confidence']:.0%})")
                occ_value.pack(side=tk.LEFT)
        
        # Affinity predictions
        if "affinity_predictions" in predictions and predictions["affinity_predictions"]:
            affinity_frame = ttk.LabelFrame(right_frame, text="Affinity Predictions", padding=10)
            affinity_frame.pack(fill=tk.X, pady=10)
            
            for affinity in predictions["affinity_predictions"]:
                aff_category = ttk.Frame(affinity_frame)
                aff_category.pack(fill=tk.X, pady=5)
                
                category_label = ttk.Label(aff_category, 
                                        text=affinity["category"],
                                        font=("Helvetica", 11, "bold"))
                category_label.pack(anchor=tk.W)
                
                if "affinities" in affinity and affinity["affinities"]:
                    affinities_text = ", ".join(affinity["affinities"])
                    affinities_label = ttk.Label(aff_category, text=affinities_text, wraplength=350)
                    affinities_label.pack(anchor=tk.W, pady=2)
                
                if "confidence" in affinity:
                    conf_frame = ttk.Frame(aff_category)
                    conf_frame.pack(fill=tk.X, pady=2)
                    
                    conf_label = ttk.Label(conf_frame, text="Confidence: ", width=12, anchor=tk.W)
                    conf_label.pack(side=tk.LEFT)
                    
                    conf_bar = ttk.Progressbar(conf_frame, 
                                            value=int(affinity["confidence"]*100), 
                                            length=100)
                    conf_bar.pack(side=tk.LEFT, padx=5)
                    
                    conf_value = ttk.Label(conf_frame, text=f"{affinity['confidence']:.0%}")
                    conf_value.pack(side=tk.LEFT)
    
    def _start_analysis(self):
        """Start the analysis process"""
        platform = self.platform_var.get()
        profile_id = self.profile_var.get()
        
        if not profile_id:
            messagebox.showerror("Input Error", "Please enter a profile ID")
            return
        
        # Show progress frame
        for widget in self.input_frame.winfo_children():
            widget.pack_forget()
        
        self.progress_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=100)
        self.progress_var.set(0)
        self.progress_status_var.set("Initializing analysis...")
        
        # Start analysis in background thread
        self.analysis_thread = threading.Thread(target=self._run_analysis, 
                                             args=(platform, profile_id))
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
        # Schedule progress updates
        self._update_progress()
    
    def _run_analysis(self, platform, profile_id):
        """Run the analysis in background thread"""
        try:
            # Wait for analyzer to be ready
            while self.analyzer is None:
                time.sleep(0.1)
            
            # Run the analysis
            self.analysis_results = self.analyzer.analyze_profile(platform, profile_id)
            
            # Signal completion
            self.progress_var.set(100)
            self.progress_status_var.set("Analysis complete!")
            
            # Schedule UI update for results
            self.after(1000, self._show_results)
        except Exception as e:
            # Handle errors
            self.progress_status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Analysis Error", f"An error occurred during analysis: {str(e)}")
            
            # Go back to input form
            self.after(1000, self._reset_form)
    
    def _update_progress(self):
        """Update progress bar during analysis"""
        if self.progress_var.get() < 100:
            # If analysis is still running
            current = self.progress_var.get()
            
            # Simulate progress - in a real app, this would get actual progress
            if current < 90:
                increment = min(10, 90 - current)
                self.progress_var.set(current + increment)
                
                # Update status message periodically
                if current < 20:
                    self.progress_status_var.set("Collecting profile data...")
                elif current < 50:
                    self.progress_status_var.set("Analyzing content...")
                elif current < 70:
                    self.progress_status_var.set("Evaluating authenticity...")
                elif current < 85:
                    self.progress_status_var.set("Generating predictions...")
            
            # Schedule next update
            self.after(500, self._update_progress)
    
    def _show_results(self):
        """Show the analysis results"""
        # Hide progress frame and go back to notebook
        self.progress_frame.pack_forget()
        self._reset_input_frame()
        
        # Setup results tabs
        self._setup_results_summary()
        self._setup_timeline_tab()
        self._setup_traits_tab()
        self._setup_writing_tab()
        self._setup_authenticity_tab()
        self._setup_predictions_tab()
        
        # Enable all tabs
        for i in range(self.notebook.index("end")):
            self.notebook.tab(i, state="normal")
        
        # Switch to results tab
        self.notebook.select(1)  # Summary tab
        
        # Update status
        self.status_var.set(f"Analysis completed for {self.profile_var.get()} on {self.platform_var.get()}")
        
        # Offer to save
        save = messagebox.askyesno("Analysis Complete", 
                                 "Analysis has been completed. Would you like to save the results?")
        if save:
            self._save_results()
    
    def _reset_input_frame(self):
        """Reset the input frame to initial state"""
        for widget in self.input_frame.winfo_children():
            if widget != self.progress_frame:
                widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    def _clear_form(self):
        """Clear the input form"""
        self.profile_var.set("")
    
    def _reset_analysis(self):
        """Reset the application for a new analysis"""
        # Clear current results
        self.analysis_results = None
        
        # Reset tabs
        self._setup_results_summary()
        self._setup_timeline_tab()
        self._setup_traits_tab()
        self._setup_writing_tab()
        self._setup_authenticity_tab()
        self._setup_predictions_tab()
        
        # Disable result tabs
        for i in range(1, self.notebook.index("end")):
            self.notebook.tab(i, state="disabled")
        
        # Switch to input tab
        self.notebook.select(0)
        
        # Reset form
        self._clear_form()
        
        # Update status
        self.status_var.set("Ready for new analysis")
    
    def _load_results(self):
        """Load analysis results from file"""
        file_path = filedialog.askopenfilename(
            title="Load Analysis Results",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                self.analysis_results = json.load(f)
            
            # Setup results tabs
            self._setup_results_summary()
            self._setup_timeline_tab()
            self._setup_traits_tab()
            self._setup_writing_tab()
            self._setup_authenticity_tab()
            self._setup_predictions_tab()
            
            # Enable all tabs
            for i in range(self.notebook.index("end")):
                self.notebook.tab(i, state="normal")
            
            # Switch to results tab
            self.notebook.select(1)  # Summary tab
            
            # Update status
            self.status_var.set(f"Loaded results from {os.path.basename(file_path)}")
            
            # Update profile input
            if "metadata" in self.analysis_results:
                metadata = self.analysis_results["metadata"]
                if "platform" in metadata:
                    self.platform_var.set(metadata["platform"])
                if "profile_id" in metadata:
                    self.profile_var.set(metadata["profile_id"])
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading results: {str(e)}")
    
    def _save_results(self):
        """Save analysis results to file"""
        if not self.analysis_results:
            messagebox.showerror("Save Error", "No analysis results to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Analysis Results",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.analysis_results, f, indent=2)
            
            self.status_var.set(f"Results saved to {os.path.basename(file_path)}")
            messagebox.showinfo("Save Complete", f"Results saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving results: {str(e)}")
    
    def _show_config(self):
        """Show configuration dialog"""
        # This would open a configuration dialog
        messagebox.showinfo("Configuration", "Configuration dialog would appear here")
    
    def _show_docs(self):
        """Show documentation"""
        # This would open documentation
        messagebox.showinfo("Documentation", "Documentation would appear here")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
        SocialInsight: Social Media Profile Analyzer
        Version 1.0.0
        
        An open-source tool for analyzing public social media profiles.
        
        Features:
        - Data collection from multiple platforms
        - Content analysis
        - Personality trait identification
        - Writing style analysis
        - Authenticity evaluation
        - Prediction generation
        
        This software is for educational and research purposes only.
        Use responsibly and respect privacy.
        """
        
        messagebox.showinfo("About SocialInsight", about_text)


# Entry point
def main():
    """Main application entry point"""
    app = AnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    # Add required imports at top
    import time
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    
    main()