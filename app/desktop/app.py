# ProfileScope: GUI Implementation
# A user-friendly interface for the Social Media Profile Analyzer

import sys
import os
import json
import threading
import datetime
import time  # Add missing time import
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

# Configure for maximum compatibility
import os
import sys

# Set environment variables to avoid Qt conflicts
os.environ['QT_API'] = 'tkinter'
os.environ['MPLBACKEND'] = 'TkAgg'

# Configure matplotlib before importing tkinter
import matplotlib
matplotlib.use("TkAgg")

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Import matplotlib plotting with error handling
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Matplotlib charts unavailable: {e}")
    MATPLOTLIB_AVAILABLE = False

# Fix for macOS compatibility
import platform
import sys

def check_macos_compatibility():
    """Check macOS compatibility without strict version requirements"""
    if platform.system() == "Darwin":  # macOS
        try:
            version = platform.mac_ver()[0]
            if version:
                # Parse version properly
                version_parts = version.split('.')
                major = int(version_parts[0])
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                
                # macOS 10.14+ should work fine (Mojave and later)
                if major >= 11 or (major == 10 and minor >= 14):
                    return True
                else:
                    print(f"⚠️  Warning: macOS {version} detected. Some features may not work optimally.")
                    return True  # Allow to continue anyway
            else:
                print("⚠️  Warning: Could not detect macOS version.")
                return True  # Allow to continue
        except Exception as e:
            print(f"⚠️  Warning: Error checking macOS version: {e}")
            return True  # Allow to continue
    return True

# Import the analyzer core
from app.core.analyzer import SocialMediaAnalyzer


class AnalyzerApp(tk.Tk):
    """Main application window for ProfileScope"""

    def __init__(self):
        # Check macOS compatibility
        if not check_macos_compatibility():
            print("❌ macOS compatibility check failed")
            sys.exit(1)
            
        # Ensure the Tk root is properly initialized for matplotlib
        super().__init__()

        # Make sure the window is visible on macOS - with error handling
        try:
            self.update_idletasks()
            self.lift()
            # Only set topmost on supported systems
            if platform.system() == "Darwin":
                try:
                    self.attributes("-topmost", True)
                    self.after_idle(self.attributes, "-topmost", False)
                except tk.TclError:
                    # Fallback for older macOS versions
                    pass
            # Explicitly process any pending events before continuing
            self.update()
        except Exception as e:
            print(f"⚠️  Warning: Window initialization issue: {e}")
            # Continue anyway

        # Initialize app window
        self.title("ProfileScope: Social Media Profile Analyzer")
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
            "bg_light": "#f5f5f5",
        }

        # Initialize variables
        self.status_var = tk.StringVar()
        self.status_var.set("Starting...")
        self.init_error = None

        # Get the root directory of the project
        import os

        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.config_path = os.path.join(project_root, "config", "config.json")

        # Configure styles
        self.style.configure(
            "Primary.TButton",
            background=self.colors["primary"],
            foreground=self.colors["white"],
            font=("Helvetica", 11, "bold"),
        )

        self.style.configure(
            "Secondary.TButton",
            background=self.colors["secondary"],
            foreground=self.colors["white"],
        )

        self.style.configure(
            "TitleLabel.TLabel", font=("Helvetica", 16, "bold"), padding=10
        )

        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), padding=5)

        self.style.configure(
            "Subheader.TLabel", font=("Helvetica", 12, "bold"), padding=5
        )

        # Create main UI
        self._create_menu()
        self._create_main_frame()

        # Status bar
        self.status_bar = ttk.Label(
            self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize our analyzer in background
        self.analyzer = None
        self.analysis_results = None
        self.init_analyzer_thread = threading.Thread(target=self._init_analyzer)
        self.init_analyzer_thread.daemon = True
        self.init_analyzer_thread.start()

        # Check initialization status periodically
        self.after(100, self._check_init_status)

    def _init_analyzer(self):
        """Initialize the analyzer in background thread"""
        self.status_var.set("Initializing analyzer...")
        try:
            self.analyzer = SocialMediaAnalyzer(config_path=self.config_path)
            self.status_var.set("Ready")
        except Exception as e:
            self.init_error = str(e)
            self.status_var.set(f"Error initializing analyzer")

    def _check_init_status(self):
        """Check initialization status and show error if any"""
        if self.init_error:
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize analyzer: {self.init_error}",
            )
            self.init_error = None
        elif not self.analyzer:
            # Keep checking if still initializing
            self.after(100, self._check_init_status)

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
        title_label = ttk.Label(
            self.input_frame,
            text="Analyze Social Media Profile",
            style="TitleLabel.TLabel",
        )
        title_label.pack(pady=20)

        # Input form
        input_form = ttk.Frame(self.input_frame, padding=20)
        input_form.pack(fill=tk.BOTH, expand=True, padx=50)

        # Platform selection
        platform_frame = ttk.Frame(input_form)
        platform_frame.pack(fill=tk.X, pady=10)

        platform_label = ttk.Label(
            platform_frame, text="Platform:", width=15, anchor=tk.W
        )
        platform_label.pack(side=tk.LEFT)

        self.platform_var = tk.StringVar()
        self.platform_var.set("twitter")

        platform_combo = ttk.Combobox(
            platform_frame,
            textvariable=self.platform_var,
            state="readonly",
            values=["twitter", "facebook"],
        )
        platform_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Profile ID input
        profile_frame = ttk.Frame(input_form)
        profile_frame.pack(fill=tk.X, pady=10)

        profile_label = ttk.Label(
            profile_frame, text="Profile ID:", width=15, anchor=tk.W
        )
        profile_label.pack(side=tk.LEFT)

        self.profile_var = tk.StringVar()
        profile_entry = ttk.Entry(profile_frame, textvariable=self.profile_var)
        profile_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Collection method frame
        method_frame = ttk.LabelFrame(
            input_form, text="Data Collection Method", padding=10
        )
        method_frame.pack(fill=tk.X, pady=10)

        self.collection_method = tk.StringVar()
        self.collection_method.set("api")

        api_radio = ttk.Radiobutton(
            method_frame,
            text="API Access (Recommended)",
            variable=self.collection_method,
            value="api",
        )
        api_radio.pack(anchor=tk.W, pady=5)

        web_radio = ttk.Radiobutton(
            method_frame,
            text="Web Scraping",
            variable=self.collection_method,
            value="web",
        )
        web_radio.pack(anchor=tk.W, pady=5)

        manual_radio = ttk.Radiobutton(
            method_frame,
            text="Manual Input",
            variable=self.collection_method,
            value="manual",
        )
        manual_radio.pack(anchor=tk.W, pady=5)

        # Options frame
        options_frame = ttk.LabelFrame(input_form, text="Analysis Options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)

        # Include sentiment analysis
        self.sentiment_var = tk.BooleanVar(value=True)
        sentiment_check = ttk.Checkbutton(
            options_frame,
            text="Include sentiment analysis",
            variable=self.sentiment_var,
        )
        sentiment_check.pack(anchor=tk.W, pady=5)

        # Include authenticty analysis
        self.authenticity_var = tk.BooleanVar(value=True)
        authenticity_check = ttk.Checkbutton(
            options_frame,
            text="Include authenticity analysis",
            variable=self.authenticity_var,
        )
        authenticity_check.pack(anchor=tk.W, pady=5)

        # Include predictions
        self.predictions_var = tk.BooleanVar(value=True)
        predictions_check = ttk.Checkbutton(
            options_frame, text="Include predictions", variable=self.predictions_var
        )
        predictions_check.pack(anchor=tk.W, pady=5)

        # Action buttons
        button_frame = ttk.Frame(input_form)
        button_frame.pack(fill=tk.X, pady=20)

        analyze_button = ttk.Button(
            button_frame,
            text="Start Analysis",
            style="Primary.TButton",
            command=self._start_analysis,
        )
        analyze_button.pack(side=tk.RIGHT, padx=5)

        clear_button = ttk.Button(
            button_frame,
            text="Clear",
            style="Secondary.TButton",
            command=self._clear_form,
        )
        clear_button.pack(side=tk.RIGHT, padx=5)

        # Progress frame (initially hidden)
        self.progress_frame = ttk.Frame(self.input_frame)

        progress_label = ttk.Label(self.progress_frame, text="Analysis in progress...")
        progress_label.pack(pady=10)

        self.progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode="determinate",
            variable=self.progress_var,
        )
        progress_bar.pack(pady=10, fill=tk.X, padx=50)

        self.progress_status_var = tk.StringVar()
        self.progress_status_var.set("Initializing...")
        progress_status = ttk.Label(
            self.progress_frame, textvariable=self.progress_status_var
        )
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
        scrollbar = ttk.Scrollbar(
            self.results_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Check if this is mock data
        mock_data = False
        if (
            "content_analysis" in self.analysis_results
            and "mock_data_disclaimer" in self.analysis_results["content_analysis"]
        ):
            mock_data = True

        # Check for API error messages
        api_errors = None
        if (
            "metadata" in self.analysis_results
            and "platform" in self.analysis_results["metadata"]
        ):
            platform = self.analysis_results["metadata"]["platform"]
            if (
                f"{platform}_data" in self.analysis_results
                and "metadata" in self.analysis_results[f"{platform}_data"]
            ):
                profile_metadata = self.analysis_results[f"{platform}_data"]["metadata"]
                if "api_errors" in profile_metadata and profile_metadata["api_errors"]:
                    api_errors = profile_metadata["api_errors"]

        # Display mock data warning if applicable
        if mock_data:
            mock_frame = ttk.Frame(scrollable_frame, padding=10)
            mock_frame.pack(fill=tk.X, padx=20, pady=10)

            warning_icon = ttk.Label(mock_frame, text="⚠️", font=("Arial", 24))
            warning_icon.pack(side=tk.LEFT, padx=10)

            disclaimer_text = self.analysis_results["content_analysis"][
                "mock_data_disclaimer"
            ]
            mock_text = ttk.Label(
                mock_frame,
                text=disclaimer_text,
                wraplength=600,
                foreground=self.colors["warning"],
            )
            mock_text.pack(fill=tk.X, expand=True, padx=10)

        # Display API error details if available
        if api_errors:
            error_frame = ttk.Frame(scrollable_frame, padding=10)
            error_frame.pack(fill=tk.X, padx=20, pady=5)

            error_icon = ttk.Label(error_frame, text="❌", font=("Arial", 20))
            error_icon.pack(side=tk.LEFT, padx=10)

            error_title = ttk.Label(
                error_frame,
                text="API Error Details:",
                font=("Helvetica", 11, "bold"),
            )
            error_title.pack(side=tk.LEFT, padx=5)

            errors_container = ttk.Frame(scrollable_frame, padding=(40, 5, 20, 10))
            errors_container.pack(fill=tk.X, padx=20)

            for error_msg in api_errors:
                error_detail = ttk.Label(
                    errors_container,
                    text=f"• {error_msg}",
                    wraplength=600,
                    foreground=self.colors["danger"],
                )
                error_detail.pack(anchor=tk.W, pady=2)

        # Display general error message if available in the results
        elif "error" in self.analysis_results:
            error_frame = ttk.Frame(scrollable_frame, padding=10)
            error_frame.pack(fill=tk.X, padx=20, pady=5)

            error_icon = ttk.Label(error_frame, text="❌", font=("Arial", 20))
            error_icon.pack(side=tk.LEFT, padx=10)

            error_message = self.analysis_results["error"]
            error_text = ttk.Label(
                error_frame,
                text=error_message,
                wraplength=600,
                foreground=self.colors["danger"],
                font=("Helvetica", 11, "bold"),
            )
            error_text.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Display success message if analysis was successful and no errors
        elif (
            not api_errors
            and "metadata" in self.analysis_results
            and "profile_id" in self.analysis_results["metadata"]
        ):
            success_frame = ttk.Frame(scrollable_frame, padding=10)
            success_frame.pack(fill=tk.X, padx=20, pady=5)

            success_icon = ttk.Label(success_frame, text="✅", font=("Arial", 20))
            success_icon.pack(side=tk.LEFT, padx=10)

            username = self.analysis_results["metadata"]["profile_id"]
            success_message = f"Analysis for {username} completed successfully!"
            success_text = ttk.Label(
                success_frame,
                text=success_message,
                wraplength=600,
                foreground=self.colors["success"],
                font=("Helvetica", 11),
            )
            success_text.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Profile metadata
        metadata = self.analysis_results["metadata"]

        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        platform_icon = ttk.Label(header_frame, text="🔍")  # Platform icon
        platform_icon.config(font=("Arial", 24))
        platform_icon.pack(side=tk.LEFT, padx=10)

        title = ttk.Label(
            header_frame,
            text=f"Profile Analysis: {metadata['profile_id']}"
            + (" (MOCK DATA)" if mock_data else ""),
            style="TitleLabel.TLabel",
        )
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Summary section - key part that was missing
        if (
            "content_analysis" in self.analysis_results
            and "summary" in self.analysis_results["content_analysis"]
        ):
            summary = self.analysis_results["content_analysis"]["summary"]

            # Main summary card
            summary_frame = ttk.LabelFrame(
                scrollable_frame, text="Profile Summary", padding=15
            )
            summary_frame.pack(fill=tk.X, padx=20, pady=10)

            # Profile overview
            if "profile_overview" in summary:
                overview_label = ttk.Label(
                    summary_frame,
                    text=summary["profile_overview"],
                    wraplength=700,
                    font=("Helvetica", 12),
                )
                overview_label.pack(anchor=tk.W, pady=5)

            # Content overview
            if "content_overview" in summary:
                content_label = ttk.Label(
                    summary_frame,
                    text=summary["content_overview"],
                    wraplength=700,
                    font=("Helvetica", 12),
                )
                content_label.pack(anchor=tk.W, pady=5)

            # Personality overview
            if "personality_overview" in summary and summary["personality_overview"]:
                personality_label = ttk.Label(
                    summary_frame,
                    text=summary["personality_overview"],
                    wraplength=700,
                    font=("Helvetica", 12),
                )
                personality_label.pack(anchor=tk.W, pady=5)

            # Key metrics section
            metrics_frame = ttk.LabelFrame(
                scrollable_frame, text="Key Metrics", padding=15
            )
            metrics_frame.pack(fill=tk.X, padx=20, pady=10)

            # Create columns for key metrics
            metrics_columns = ttk.Frame(metrics_frame)
            metrics_columns.pack(fill=tk.X, pady=5)

            # Left column
            left_metrics = ttk.Frame(metrics_columns)
            left_metrics.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Post count
            if "post_count" in summary:
                post_count_frame = ttk.Frame(left_metrics)
                post_count_frame.pack(fill=tk.X, pady=5)

                post_count_label = ttk.Label(
                    post_count_frame, text="Posts Analyzed:", width=18, anchor=tk.W
                )
                post_count_label.pack(side=tk.LEFT)

                post_count_value = ttk.Label(
                    post_count_frame,
                    text=str(summary["post_count"]),
                    font=("Helvetica", 11, "bold"),
                )
                post_count_value.pack(side=tk.LEFT)

            # Activity level
            if "activity_level" in summary:
                activity_frame = ttk.Frame(left_metrics)
                activity_frame.pack(fill=tk.X, pady=5)

                activity_label = ttk.Label(
                    activity_frame, text="Activity Level:", width=18, anchor=tk.W
                )
                activity_label.pack(side=tk.LEFT)

                activity_value = ttk.Label(
                    activity_frame,
                    text=summary["activity_level"].replace("_", " ").title(),
                    font=("Helvetica", 11, "bold"),
                )
                activity_value.pack(side=tk.LEFT)

            # Right column
            right_metrics = ttk.Frame(metrics_columns)
            right_metrics.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            # Main topics
            if "main_topics" in summary and summary["main_topics"]:
                topics_frame = ttk.Frame(right_metrics)
                topics_frame.pack(fill=tk.X, pady=5)

                topics_label = ttk.Label(
                    topics_frame, text="Main Topics:", width=18, anchor=tk.W
                )
                topics_label.pack(side=tk.LEFT)

                topics_value = ttk.Label(
                    topics_frame,
                    text=", ".join(summary["main_topics"]),
                    font=("Helvetica", 11, "bold"),
                )
                topics_value.pack(side=tk.LEFT)

            # General sentiment
            if "general_sentiment" in summary:
                sentiment_frame = ttk.Frame(right_metrics)
                sentiment_frame.pack(fill=tk.X, pady=5)

                sentiment_label = ttk.Label(
                    sentiment_frame, text="General Sentiment:", width=18, anchor=tk.W
                )
                sentiment_label.pack(side=tk.LEFT)

                sentiment_value = ttk.Label(
                    sentiment_frame,
                    text=summary["general_sentiment"].replace("_", " ").title(),
                    font=("Helvetica", 11, "bold"),
                )
                sentiment_value.pack(side=tk.LEFT)
        else:
            # No summary available
            no_summary_label = ttk.Label(
                scrollable_frame,
                text="No summary information available for this profile",
                font=("Helvetica", 12),
            )
            no_summary_label.pack(pady=20)

        # Overview Metrics - Display key metrics from content and authenticity analysis
        metrics_section = ttk.LabelFrame(
            scrollable_frame, text="Analysis Overview", padding=15
        )
        metrics_section.pack(fill=tk.X, padx=20, pady=10)

        metrics_grid = ttk.Frame(metrics_section)
        metrics_grid.pack(fill=tk.X, pady=10)

        # Create 2x2 grid for key metrics
        metrics = []

        # Add authenticity score if available
        if (
            "authenticity_analysis" in self.analysis_results
            and "overall_authenticity" in self.analysis_results["authenticity_analysis"]
        ):
            try:
                auth_score = self.analysis_results["authenticity_analysis"][
                    "overall_authenticity"
                ]["score"]
                metrics.append(
                    {
                        "name": "Authenticity Score",
                        "value": f"{auth_score:.0%}",
                        "icon": "🔒" if auth_score > 0.7 else "⚠️",
                        "color": (
                            self.colors["success"]
                            if auth_score > 0.7
                            else self.colors["warning"]
                        ),
                    }
                )
            except (KeyError, TypeError):
                pass

        # Add posting frequency
        if (
            "content_analysis" in self.analysis_results
            and "posting_patterns" in self.analysis_results["content_analysis"]
        ):
            try:
                frequency = self.analysis_results["content_analysis"][
                    "posting_patterns"
                ]["frequency"]
                metrics.append(
                    {
                        "name": "Posting Frequency",
                        "value": f"{frequency.get('daily_average', 0):.1f}/day",
                        "icon": "📊",
                        "color": self.colors["primary"],
                    }
                )
            except (KeyError, TypeError):
                pass

        # Add sentiment if available
        if (
            "content_analysis" in self.analysis_results
            and "sentiment" in self.analysis_results["content_analysis"]
        ):
            try:
                sentiment = self.analysis_results["content_analysis"]["sentiment"][
                    "overall_sentiment"
                ]
                if sentiment.get("label") == "positive":
                    metrics.append(
                        {
                            "name": "Overall Sentiment",
                            "value": "Positive",
                            "icon": "😊",
                            "color": self.colors["success"],
                        }
                    )
                elif sentiment.get("label") == "negative":
                    metrics.append(
                        {
                            "name": "Overall Sentiment",
                            "value": "Negative",
                            "icon": "😔",
                            "color": self.colors["danger"],
                        }
                    )
                else:
                    metrics.append(
                        {
                            "name": "Overall Sentiment",
                            "value": "Neutral",
                            "icon": "😐",
                            "color": self.colors["secondary"],
                        }
                    )
            except (KeyError, TypeError):
                pass

        # Add account age if available
        if (
            "authenticity_analysis" in self.analysis_results
            and "components" in self.analysis_results["authenticity_analysis"]
        ):
            try:
                age_score = self.analysis_results["authenticity_analysis"][
                    "components"
                ]["account_age"]
                account_age_label = (
                    "New Account" if age_score < 0.5 else "Established Account"
                )
                metrics.append(
                    {
                        "name": "Account Age",
                        "value": account_age_label,
                        "icon": "🗓️",
                        "color": self.colors["primary"],
                    }
                )
            except (KeyError, TypeError):
                pass

        # Create metric cards in grid
        row, col = 0, 0
        for metric in metrics:
            metric_card = ttk.Frame(metrics_grid, padding=10, relief=tk.GROOVE)
            metric_card.grid(row=row, column=col, padx=10, pady=10, sticky=tk.NSEW)

            # Icon
            icon_label = ttk.Label(metric_card, text=metric["icon"], font=("Arial", 18))
            icon_label.pack(anchor=tk.CENTER)

            # Metric name
            name_label = ttk.Label(metric_card, text=metric["name"])
            name_label.pack(anchor=tk.CENTER)

            # Metric value
            value_label = ttk.Label(
                metric_card,
                text=metric["value"],
                font=("Helvetica", 14, "bold"),
                foreground=metric["color"],
            )
            value_label.pack(anchor=tk.CENTER, pady=5)

            # Update grid position
            col += 1
            if col > 1:
                col = 0
                row += 1

        # Configure grid columns to be equal width
        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)

    def _setup_timeline_tab(self):
        """Set up the timeline visualization tab"""
        # Clear existing widgets
        for widget in self.timeline_frame.winfo_children():
            widget.destroy()

        if (
            not self.analysis_results
            or "content_analysis" not in self.analysis_results
            or "timeline" not in self.analysis_results["content_analysis"]
        ):
            label = ttk.Label(self.timeline_frame, text="No timeline data available")
            label.pack(pady=50)
            return

        # Get timeline data
        timeline_data = self.analysis_results["content_analysis"]["timeline"]

        # Main timeline container with scrolling
        timeline_canvas = tk.Canvas(self.timeline_frame)
        timeline_scrollbar = ttk.Scrollbar(
            self.timeline_frame, orient="vertical", command=timeline_canvas.yview
        )
        timeline_scrollable = ttk.Frame(timeline_canvas)

        timeline_scrollable.bind(
            "<Configure>",
            lambda e: timeline_canvas.configure(
                scrollregion=timeline_canvas.bbox("all")
            ),
        )

        timeline_canvas.create_window((0, 0), window=timeline_scrollable, anchor="nw")
        timeline_canvas.configure(yscrollcommand=timeline_scrollbar.set)

        timeline_canvas.pack(side="left", fill="both", expand=True)
        timeline_scrollbar.pack(side="right", fill="y")

        # Title
        title = ttk.Label(
            timeline_scrollable, text="Activity Timeline", style="TitleLabel.TLabel"
        )
        title.pack(pady=20)

        # Timeline frame
        tl_frame = ttk.Frame(timeline_scrollable, padding=10)
        tl_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Check if we have any timeline entries
        if not timeline_data or len(timeline_data) == 0:
            empty_label = ttk.Label(tl_frame, text="No timeline events found")
            empty_label.pack(pady=20)
            return

        # Create axis line
        axis_frame = ttk.Frame(tl_frame)
        axis_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Sort timeline entries by date if available
        try:
            # Sort if date is available
            from datetime import datetime

            timeline_data = sorted(
                timeline_data,
                key=lambda x: datetime.strptime(
                    x.get("date", "2000-01-01"), "%Y-%m-%d"
                ),
                reverse=True,  # Most recent first
            )
        except:
            # If sorting fails, use as is
            pass

        # Add timeline entries
        for i, event in enumerate(timeline_data):
            event_frame = ttk.Frame(axis_frame)
            event_frame.pack(fill=tk.X, pady=5)

            # Date indicator
            date_frame = ttk.Frame(event_frame, width=100)
            date_frame.pack(side=tk.LEFT, padx=10)

            if "date" in event:
                date_label = ttk.Label(
                    date_frame,
                    text=event["date"],
                    font=("Helvetica", 10, "bold"),
                    foreground=self.colors["primary"],
                )
                date_label.pack(anchor=tk.E)

            # Timeline node
            node_canvas = tk.Canvas(
                event_frame,
                width=30,
                height=30,
                bg=self.colors["bg_light"],
                highlightthickness=0,
            )
            node_canvas.pack(side=tk.LEFT)

            # Draw node
            node_canvas.create_oval(10, 5, 25, 20, fill=self.colors["primary"])

            # Draw line to next node if not last
            if i < len(timeline_data) - 1:
                node_canvas.create_line(
                    17.5, 20, 17.5, 35, fill=self.colors["primary"], width=2
                )

            # Event content
            content_frame = ttk.Frame(event_frame)
            content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

            # Event type
            if "type" in event:
                event_type = (
                    event["type"].replace("_", " ").title()
                    if isinstance(event["type"], str)
                    else "Event"
                )
                type_label = ttk.Label(
                    content_frame, text=event_type, font=("Helvetica", 11, "bold")
                )
                type_label.pack(anchor=tk.W)

            # Event description
            if "description" in event:
                desc_label = ttk.Label(
                    content_frame, text=event["description"], wraplength=600
                )
                desc_label.pack(anchor=tk.W, pady=2)

            # Additional details if available
            details_frame = ttk.Frame(content_frame)

            has_details = False
            for key, value in event.items():
                if key not in ["date", "type", "description"] and value:
                    has_details = True
                    key_label = ttk.Label(
                        details_frame,
                        text=f"{key.replace('_', ' ').title()}: ",
                        width=15,
                        anchor=tk.W,
                        font=("Helvetica", 10, "bold"),
                    )
                    key_label.pack(side=tk.LEFT)

                    value_str = (
                        str(value) if not isinstance(value, list) else ", ".join(value)
                    )
                    value_label = ttk.Label(
                        details_frame, text=value_str, wraplength=450
                    )
                    value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            if has_details:
                details_frame.pack(anchor=tk.W, pady=5)

        # Add timeline visualization (optional)
        if len(timeline_data) >= 3:
            # Try to create activity frequency chart
            try:
                # Extract dates and create frequency data
                from datetime import datetime
                from collections import Counter
                import matplotlib.dates as mdates

                # Get dates from timeline
                dates = []
                for event in timeline_data:
                    if "date" in event:
                        try:
                            date = datetime.strptime(event["date"], "%Y-%m-%d")
                            dates.append(date)
                        except:
                            pass

                if dates:
                    # Create a frequency chart
                    viz_frame = ttk.LabelFrame(
                        timeline_scrollable, text="Activity Frequency", padding=10
                    )
                    viz_frame.pack(fill=tk.X, padx=20, pady=20)

                    fig = plt.Figure(figsize=(8, 3), dpi=100)
                    ax = fig.add_subplot(111)

                    # Plot frequency
                    ax.hist(dates, bins=20, color=self.colors["primary"], alpha=0.7)
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Number of Events")

                    # Format date axis
                    date_formatter = mdates.DateFormatter("%Y-%m")
                    ax.xaxis.set_major_formatter(date_formatter)
                    fig.autofmt_xdate()

                    # Add chart to frame
                    chart = FigureCanvasTkAgg(fig, viz_frame)
                    chart.get_tk_widget().pack(fill=tk.X, expand=True)

            except Exception as e:
                print(f"Error creating timeline visualization: {str(e)}")

    def _setup_traits_tab(self):
        """Set up the personality traits and interests tab"""
        # Clear existing widgets
        for widget in self.traits_frame.winfo_children():
            widget.destroy()

        if not self.analysis_results or "content_analysis" not in self.analysis_results:
            label = ttk.Label(
                self.traits_frame, text="No personality traits data available"
            )
            label.pack(pady=50)
            return

        content = self.analysis_results.get("content_analysis", {})

        # Title
        title = ttk.Label(
            self.traits_frame, text="Personality Profile", style="TitleLabel.TLabel"
        )
        title.pack(pady=20)

        # Create a two-column layout
        columns_frame = ttk.Frame(self.traits_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left column - Traits
        traits_frame = ttk.LabelFrame(
            columns_frame, text="Personality Traits", padding=10
        )
        traits_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Check if we have personality traits
        if "personality_traits" in content and content["personality_traits"]:
            traits = content["personality_traits"]

            # Create radar chart for personality traits
            traits_fig = plt.Figure(figsize=(5, 4), dpi=100)
            traits_ax = traits_fig.add_subplot(111, polar=True)

            # Get categories and values from traits
            categories = list(traits.keys())
            values = list(traits.values())

            # Calculate angles for each category
            n_cats = len(categories)
            angles = [n / float(n_cats) * 2 * np.pi for n in range(n_cats)]

            # Close the polygon
            values.append(values[0])
            angles.append(angles[0])

            # Plot
            traits_ax.plot(angles, values, linewidth=2, linestyle="solid")
            traits_ax.fill(angles, values, alpha=0.3)

            # Set category labels
            traits_ax.set_xticks(angles[:-1])
            traits_ax.set_xticklabels(categories)

            # Create canvas for chart
            traits_chart = FigureCanvasTkAgg(traits_fig, traits_frame)
            traits_chart.get_tk_widget().pack(pady=10)

            # Add legend or additional info
            legend_frame = ttk.Frame(traits_frame)
            legend_frame.pack(fill=tk.X, pady=10)

            for trait, value in traits.items():
                trait_frame = ttk.Frame(legend_frame)
                trait_frame.pack(fill=tk.X, pady=2)

                trait_label = ttk.Label(
                    trait_frame,
                    text=trait.replace("_", " ").title(),
                    width=20,
                    anchor=tk.W,
                )
                trait_label.pack(side=tk.LEFT)

                trait_bar = ttk.Progressbar(
                    trait_frame, value=int(value * 100), length=100
                )
                trait_bar.pack(side=tk.LEFT, padx=5)

                trait_value = ttk.Label(trait_frame, text=f"{value:.2f}")
                trait_value.pack(side=tk.LEFT)
        else:
            no_traits = ttk.Label(
                traits_frame, text="No personality trait data available"
            )
            no_traits.pack(pady=20)

        # Right column - Interests
        interests_frame = ttk.LabelFrame(
            columns_frame, text="Interests & Topics", padding=10
        )
        interests_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Check if we have interests data
        if "interests" in content and content["interests"]:
            interests = content["interests"]

            # Sort interests by confidence score (if interests are dictionaries)
            # or by direct value (if interests are simple values)
            def get_interest_value(item):
                key, value = item
                if isinstance(value, dict) and "confidence" in value:
                    return value["confidence"]  # Get confidence from dict
                elif isinstance(value, (int, float)):
                    return value  # Use direct value if it's a number
                return 0  # Default if no usable value

            sorted_interests = sorted(
                interests.items(), key=get_interest_value, reverse=True
            )

            # Create bar chart for top interests
            top_interests = sorted_interests[:8]  # Show top 8

            int_fig = plt.Figure(figsize=(5, 4), dpi=100)
            int_ax = int_fig.add_subplot(111)

            # Extract labels and values based on the type of interest values
            labels = []
            values = []

            for item in top_interests:
                key, value = item
                labels.append(key.replace("_", " ").title())

                if isinstance(value, dict) and "confidence" in value:
                    values.append(value["confidence"])
                elif isinstance(value, (int, float)):
                    values.append(value)
                else:
                    values.append(0)  # Default if no usable value

            int_ax.barh(labels, values, color=self.colors["primary"])
            int_ax.set_xlim(0, 1.0)
            int_ax.set_title("Top Interests")

            # Create canvas for chart
            int_chart = FigureCanvasTkAgg(int_fig, interests_frame)
            int_chart.get_tk_widget().pack(pady=10)

            # List all interests with scores
            list_frame = ttk.Frame(interests_frame)
            list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            # Create a canvas with scrollbar for many interests
            canvas = tk.Canvas(list_frame)
            scrollbar = ttk.Scrollbar(
                list_frame, orient="vertical", command=canvas.yview
            )
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Add all interests to the scrollable frame
            for interest, interest_value in sorted_interests:
                int_frame = ttk.Frame(scrollable_frame)
                int_frame.pack(fill=tk.X, pady=2)

                int_label = ttk.Label(
                    int_frame,
                    text=interest.replace("_", " ").title(),
                    width=20,
                    anchor=tk.W,
                )
                int_label.pack(side=tk.LEFT)

                # Get the value to display based on the type of interest_value
                display_value = 0
                if isinstance(interest_value, dict) and "confidence" in interest_value:
                    display_value = interest_value["confidence"]
                elif isinstance(interest_value, (int, float)):
                    display_value = interest_value

                int_bar = ttk.Progressbar(
                    int_frame, value=int(display_value * 100), length=100
                )
                int_bar.pack(side=tk.LEFT, padx=5)

                int_value = ttk.Label(int_frame, text=f"{display_value:.2f}")
                int_value.pack(side=tk.LEFT)
        else:
            no_interests = ttk.Label(
                interests_frame, text="No interests data available"
            )
            no_interests.pack(pady=20)

    def _setup_writing_tab(self):
        """Set up the writing style analysis tab"""
        # Clear existing widgets
        for widget in self.writing_frame.winfo_children():
            widget.destroy()

        if (
            not self.analysis_results
            or "content_analysis" not in self.analysis_results
            or "writing_style" not in self.analysis_results["content_analysis"]
        ):
            label = ttk.Label(
                self.writing_frame, text="No writing style data available"
            )
            label.pack(pady=50)
            return

        writing_style = self.analysis_results["content_analysis"]["writing_style"]

        # Main container
        main_frame = ttk.Frame(self.writing_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(
            main_frame, text="Writing Style Analysis", style="TitleLabel.TLabel"
        )
        title.pack(pady=20)

        # Create two columns
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left column - General metrics
        metrics_frame = ttk.LabelFrame(columns_frame, text="Style Metrics", padding=10)
        metrics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Create a radar chart for key metrics
        if all(
            k in writing_style
            for k in [
                "complexity",
                "formality",
                "emotional_tone",
                "vocabulary_diversity",
            ]
        ):
            metrics_fig = plt.Figure(figsize=(5, 4), dpi=100)
            metrics_ax = metrics_fig.add_subplot(111, polar=True)

            metrics = {
                "Complexity": writing_style["complexity"],
                "Formality": writing_style["formality"],
                "Emotional Tone": writing_style["emotional_tone"],
                "Vocabulary": writing_style["vocabulary_diversity"],
            }

            # Define metric_keys before using it
            metric_keys = [
                ("complexity", "Complexity"),
                ("formality", "Formality"),
                ("emotional_tone", "Emotional Tone"),
                ("vocabulary_diversity", "Vocabulary Diversity"),
            ]

        # Create metrics details
        metrics_details = ttk.Frame(metrics_frame)
        metrics_details.pack(fill=tk.X, pady=10)

        # Define metric_keys again in case the above code block didn't execute
        if not "metric_keys" in locals():
            metric_keys = [
                ("complexity", "Complexity"),
                ("formality", "Formality"),
                ("emotional_tone", "Emotional Tone"),
                ("vocabulary_diversity", "Vocabulary Diversity"),
            ]

        for key, label in metric_keys:
            if key in writing_style:
                metric_frame = ttk.Frame(metrics_details)
                metric_frame.pack(fill=tk.X, pady=2)

                metric_label = ttk.Label(
                    metric_frame, text=label, width=20, anchor=tk.W
                )
                metric_label.pack(side=tk.LEFT)

                metric_bar = ttk.Progressbar(
                    metric_frame, value=int(writing_style[key] * 100), length=100
                )
                metric_bar.pack(side=tk.LEFT, padx=5)

                metric_value = ttk.Label(metric_frame, text=f"{writing_style[key]:.0%}")
                metric_value.pack(side=tk.LEFT)

        # Other metrics as text
        other_metrics = ttk.Frame(metrics_details)
        other_metrics.pack(fill=tk.X, pady=10)

        if "average_sentence_length" in writing_style:
            sent_length = ttk.Label(
                other_metrics,
                text=f"Average sentence length: {writing_style['average_sentence_length']:.1f} words",
            )
            sent_length.pack(anchor=tk.W, pady=2)

        if "word_count" in writing_style:
            word_count = ttk.Label(
                other_metrics, text=f"Total word count: {writing_style['word_count']}"
            )
            word_count.pack(anchor=tk.W, pady=2)

        # Right column - Distinctive elements
        distinctive_frame = ttk.LabelFrame(
            columns_frame, text="Distinctive Elements", padding=10
        )
        distinctive_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Frequent words
        if "frequent_words" in writing_style and writing_style["frequent_words"]:
            freq_frame = ttk.Frame(distinctive_frame)
            freq_frame.pack(fill=tk.X, pady=10)

            freq_label = ttk.Label(
                freq_frame, text="Frequently Used Words:", style="Subheader.TLabel"
            )
            freq_label.pack(anchor=tk.W)

            # Word cloud placeholder (in a real app, could use wordcloud module)
            freq_cloud = ttk.Frame(freq_frame, height=100, relief=tk.SUNKEN)
            freq_cloud.pack(fill=tk.X, pady=5)

            words_text = ", ".join(writing_style["frequent_words"])
            words_label = ttk.Label(freq_cloud, text=words_text, wraplength=350)
            words_label.pack(padx=10, pady=10)

        # Distinctive phrases
        if (
            "distinctive_phrases" in writing_style
            and writing_style["distinctive_phrases"]
        ):
            phrase_frame = ttk.Frame(distinctive_frame)
            phrase_frame.pack(fill=tk.X, pady=10)

            phrase_label = ttk.Label(
                phrase_frame, text="Distinctive Phrases:", style="Subheader.TLabel"
            )
            phrase_label.pack(anchor=tk.W)

            phrase_list = ttk.Frame(phrase_frame)
            phrase_list.pack(fill=tk.X, pady=5)

            for i, phrase in enumerate(writing_style["distinctive_phrases"]):
                phrase_item = ttk.Label(phrase_list, text=f'"{phrase}"')
                phrase_item.pack(anchor=tk.W, pady=2)

        # Stylistic fingerprint
        if "stylistic_fingerprint" in writing_style:
            fingerprint_frame = ttk.LabelFrame(
                main_frame, text="Stylistic Fingerprint", padding=10
            )
            fingerprint_frame.pack(fill=tk.X, pady=20)

            fingerprint = writing_style["stylistic_fingerprint"]

            # Hash display with a copy button
            hash_frame = ttk.Frame(fingerprint_frame)
            hash_frame.pack(fill=tk.X, pady=10)

            hash_label = ttk.Label(
                hash_frame, text="Style Hash:", width=15, anchor=tk.W
            )
            hash_label.pack(side=tk.LEFT)

            hash_value = tk.Entry(hash_frame, width=40)
            hash_value.insert(0, fingerprint["hash"])
            hash_value.configure(state="readonly")
            hash_value.pack(side=tk.LEFT, padx=5)

            copy_button = ttk.Button(
                hash_frame,
                text="Copy",
                command=lambda: self.clipboard_clear()
                or self.clipboard_append(fingerprint["hash"]),
            )
            copy_button.pack(side=tk.LEFT, padx=5)

            # Signature features
            if "signature_features" in fingerprint:
                sig_frame = ttk.Frame(fingerprint_frame)
                sig_frame.pack(fill=tk.X, pady=10)

                sig_label = ttk.Label(
                    sig_frame, text="Signature Features:", width=15, anchor=tk.W
                )
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

        if (
            not self.analysis_results
            or "authenticity_analysis" not in self.analysis_results
        ):
            label = ttk.Label(
                self.authenticity_frame, text="No authenticity analysis data available"
            )
            label.pack(pady=50)
            return

        auth_analysis = self.analysis_results["authenticity_analysis"]

        # Main container with scrolling for better layout
        canvas = tk.Canvas(self.authenticity_frame)
        scrollbar = ttk.Scrollbar(
            self.authenticity_frame, orient="vertical", command=canvas.yview
        )
        main_frame = ttk.Frame(canvas, padding=20)

        # Configure scroll behavior
        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Allow canvas to expand and fill the authenticity frame
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title
        title = ttk.Label(
            main_frame, text="Profile Authenticity Analysis", style="TitleLabel.TLabel"
        )
        title.pack(pady=20)

        # Check for mock data disclaimer
        if "mock_data_disclaimer" in auth_analysis:
            disclaimer_frame = ttk.Frame(main_frame, padding=10)
            disclaimer_frame.pack(fill=tk.X, pady=10)

            warning_icon = ttk.Label(disclaimer_frame, text="⚠️", font=("Arial", 20))
            warning_icon.pack(side=tk.LEFT, padx=10)

            mock_text = ttk.Label(
                disclaimer_frame,
                text=auth_analysis["mock_data_disclaimer"],
                wraplength=600,
                foreground=self.colors["warning"],
            )
            mock_text.pack(fill=tk.X, expand=True, padx=10)

        # Overall authenticity score
        if "overall_authenticity" in auth_analysis:
            overall = auth_analysis["overall_authenticity"]

            overall_frame = ttk.Frame(main_frame)
            overall_frame.pack(fill=tk.X, pady=20)

            # Score gauge
            score = overall["score"]

            gauge_fig = plt.Figure(figsize=(4, 3), dpi=100)
            gauge_ax = gauge_fig.add_subplot(111, projection="polar")

            # Create a half-circle gauge
            theta = np.linspace(0, np.pi, 100)
            radius = 1.0

            # Background arc
            gauge_ax.plot(theta, [radius] * len(theta), color="lightgray", linewidth=15)

            # Score arc
            score_theta = theta[: int(score * len(theta))]
            score_radius = [radius] * len(score_theta)

            # Determine color based on score
            if score < 0.4:
                score_color = self.colors["danger"]
            elif score < 0.7:
                score_color = self.colors["warning"]
            else:
                score_color = self.colors["success"]

            gauge_ax.plot(score_theta, score_radius, color=score_color, linewidth=15)

            # Add labels
            gauge_ax.text(-0.5, 0.5, "Fake", ha="right", va="center", fontsize=12)
            gauge_ax.text(
                np.pi / 2, 1.3, "Uncertain", ha="center", va="center", fontsize=12
            )
            gauge_ax.text(
                np.pi + 0.5, 0.5, "Authentic", ha="left", va="center", fontsize=12
            )

            # Add score in center
            gauge_ax.text(
                np.pi / 2,
                0.3,
                f"Score: {score:.0%}",
                ha="center",
                va="center",
                fontsize=14,
                fontweight="bold",
            )

            # Clean up the plot
            gauge_ax.set_ylim(0, 1.5)
            gauge_ax.set_xticks([])
            gauge_ax.set_yticks([])

            # Create and configure chart widget
            gauge_canvas = FigureCanvasTkAgg(gauge_fig, overall_frame)
            gauge_canvas.draw()
            gauge_widget = gauge_canvas.get_tk_widget()
            gauge_widget.config(width=400, height=240)
            gauge_widget.pack(fill=tk.X)

            # Information below gauge
            info_frame = ttk.Frame(overall_frame)
            info_frame.pack(fill=tk.X, pady=10)

            confidence_label = ttk.Label(
                info_frame, text=f"Analysis Confidence: {overall['confidence']:.0%}"
            )
            confidence_label.pack(anchor=tk.CENTER)

            if "potential_issues" in overall and overall["potential_issues"]:
                issues_text = "Potential issues detected: " + ", ".join(
                    overall["potential_issues"]
                )
                issues_label = ttk.Label(
                    info_frame, text=issues_text, foreground=self.colors["danger"]
                )
                issues_label.pack(anchor=tk.CENTER, pady=5)

        # Authenticity assessment section
        if "assessment" in auth_analysis:
            assessment_frame = ttk.LabelFrame(
                main_frame, text="Assessment Summary", padding=15
            )
            assessment_frame.pack(fill=tk.X, pady=10)

            assessment = auth_analysis["assessment"]

            if "summary" in assessment:
                summary_label = ttk.Label(
                    assessment_frame,
                    text=assessment["summary"],
                    wraplength=700,
                    font=("Helvetica", 12),
                )
                summary_label.pack(anchor=tk.W, pady=5)

            # Risk factors
            if "risk_factors" in assessment and assessment["risk_factors"]:
                risks_frame = ttk.Frame(assessment_frame)
                risks_frame.pack(fill=tk.X, pady=10)

                risks_label = ttk.Label(
                    risks_frame, text="Risk Factors:", font=("Helvetica", 11, "bold")
                )
                risks_label.pack(anchor=tk.W)

                for risk in assessment["risk_factors"]:
                    risk_item = ttk.Label(risks_frame, text=f"• {risk}", wraplength=650)
                    risk_item.pack(anchor=tk.W, pady=2)
        # If there's no authenticity data, create mock data for display
        else:
            # Create mock authenticity data for demonstration
            mock_frame = ttk.Frame(main_frame, padding=10)
            mock_frame.pack(fill=tk.X, pady=10)

            mock_title = ttk.Label(
                mock_frame,
                text="Sample Authenticity Analysis",
                font=("Helvetica", 12, "bold"),
            )
            mock_title.pack(pady=5)

            mock_desc = ttk.Label(
                mock_frame,
                text="This is sample data to demonstrate the authenticity analysis interface.",
                wraplength=600,
            )
            mock_desc.pack(pady=5)

            # Create a sample gauge
            gauge_fig = plt.Figure(figsize=(4, 3), dpi=100)
            gauge_ax = gauge_fig.add_subplot(111, projection="polar")

            # Create a half-circle gauge
            theta = np.linspace(0, np.pi, 100)
            radius = 1.0

            # Background arc
            gauge_ax.plot(theta, [radius] * len(theta), color="lightgray", linewidth=15)

            # Score arc (sample score of 0.75)
            sample_score = 0.75
            score_theta = theta[: int(sample_score * len(theta))]
            score_radius = [radius] * len(score_theta)
            gauge_ax.plot(
                score_theta, score_radius, color=self.colors["success"], linewidth=15
            )

            # Add labels
            gauge_ax.text(-0.5, 0.5, "Fake", ha="right", va="center", fontsize=12)
            gauge_ax.text(
                np.pi / 2, 1.3, "Uncertain", ha="center", va="center", fontsize=12
            )
            gauge_ax.text(
                np.pi + 0.5, 0.5, "Authentic", ha="left", va="center", fontsize=12
            )

            # Add score in center
            gauge_ax.text(
                np.pi / 2,
                0.3,
                f"Score: {sample_score:.0%}",
                ha="center",
                va="center",
                fontsize=14,
                fontweight="bold",
            )

            # Clean up the plot
            gauge_ax.set_ylim(0, 1.5)
            gauge_ax.set_xticks([])
            gauge_ax.set_yticks([])

            # Create and configure chart widget
            gauge_canvas = FigureCanvasTkAgg(gauge_fig, mock_frame)
            gauge_canvas.draw()
            gauge_widget = gauge_canvas.get_tk_widget()
            gauge_widget.config(width=400, height=240)
            gauge_widget.pack(pady=10)

    def _setup_predictions_tab(self):
        """Set up the predictions tab"""
        # Clear existing widgets
        for widget in self.predictions_frame.winfo_children():
            widget.destroy()

        # If no analysis results available or no predictions key, create sample data
        if not self.analysis_results or "predictions" not in self.analysis_results:
            self._create_mock_predictions()
            return

        predictions = self.analysis_results["predictions"]

        # Main container with scrolling
        canvas = tk.Canvas(self.predictions_frame)
        scrollbar = ttk.Scrollbar(
            self.predictions_frame, orient="vertical", command=canvas.yview
        )
        main_frame = ttk.Frame(canvas, padding=20)

        # Configure scroll behavior
        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Allow canvas to expand and fill the predictions frame
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title and intro
        title = ttk.Label(
            main_frame, text="Profile Predictions", style="TitleLabel.TLabel"
        )
        title.pack(pady=20)

        # Check if we're using mock data and display appropriate disclaimer
        if "disclaimer" in predictions:
            disclaimer_frame = ttk.Frame(main_frame, padding=10)
            disclaimer_frame.pack(fill=tk.X, pady=10)

            info_icon = ttk.Label(disclaimer_frame, text="ℹ️", font=("Arial", 20))
            info_icon.pack(side=tk.LEFT, padx=10)

            disclaimer_text = ttk.Label(
                disclaimer_frame,
                text=predictions["disclaimer"],
                wraplength=600,
                foreground=self.colors["info"],
            )
            disclaimer_text.pack(fill=tk.X, expand=True, padx=10)

        description = ttk.Label(
            main_frame,
            text="Based on historical data and current profile analysis, the system predicts the following patterns and interests.",
            wraplength=700,
        )
        description.pack(pady=10)

        # Create a two-column layout for predictions
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left column - Future Interests
        interests_frame = ttk.LabelFrame(
            columns_frame, text="Predicted Interests", padding=10
        )
        interests_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Check for both possible future interests keys in the data structure
        future_interests = None
        if "future_interests" in predictions:
            future_interests = predictions["future_interests"]
        elif "interests" in predictions:
            future_interests = predictions["interests"]

        if future_interests:
            for interest in future_interests:
                interest_frame = ttk.Frame(interests_frame)
                interest_frame.pack(fill=tk.X, pady=5)

                # Handle different formats of interest data
                interest_name = interest.get("interest", "")
                if not interest_name and isinstance(interest, str):
                    interest_name = interest
                elif not interest_name and "label" in interest:
                    interest_name = interest["label"]

                # Only proceed if we have a valid interest name
                if interest_name:
                    interest_label = ttk.Label(
                        interest_frame,
                        text=interest_name,
                        font=("Helvetica", 11, "bold"),
                    )
                    interest_label.pack(anchor=tk.W)

                    # Get confidence value based on data structure
                    confidence = 0.7  # Default if not found
                    if "confidence" in interest:
                        confidence = interest["confidence"]
                    elif isinstance(interest, dict) and any(
                        k in interest for k in ["score", "value"]
                    ):
                        confidence = interest.get("score", interest.get("value", 0.7))

                    # Display confidence bar
                    conf_frame = ttk.Frame(interest_frame)
                    conf_frame.pack(fill=tk.X, pady=2)

                    conf_label = ttk.Label(
                        conf_frame, text="Confidence: ", width=12, anchor=tk.W
                    )
                    conf_label.pack(side=tk.LEFT)

                    conf_bar = ttk.Progressbar(
                        conf_frame, value=int(confidence * 100), length=100
                    )
                    conf_bar.pack(side=tk.LEFT, padx=5)

                    conf_value = ttk.Label(conf_frame, text=f"{confidence:.0%}")
                    conf_value.pack(side=tk.LEFT)

                    # Display reasoning if available
                    if "reasoning" in interest:
                        reason_label = ttk.Label(
                            interest_frame,
                            text=f"Reasoning: {interest['reasoning']}",
                            wraplength=350,
                        )
                        reason_label.pack(anchor=tk.W, pady=2)
                    elif "description" in interest:
                        reason_label = ttk.Label(
                            interest_frame,
                            text=interest["description"],
                            wraplength=350,
                        )
                        reason_label.pack(anchor=tk.W, pady=2)
        else:
            # If no future interests data is available
            no_interests = ttk.Label(
                interests_frame,
                text="No interest predictions available",
                wraplength=350,
            )
            no_interests.pack(pady=20)

        # Right column - Behaviors/Traits
        behaviors_frame = ttk.LabelFrame(
            columns_frame, text="Predicted Behaviors", padding=10
        )
        behaviors_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Check for various possible keys for behavior data
        behavior_data = None
        for key in ["potential_behaviors", "behavior_patterns", "personality_traits"]:
            if key in predictions:
                behavior_data = predictions[key]
                break

        if behavior_data:
            # Handle both list and dictionary formats
            behaviors_to_display = []

            if isinstance(behavior_data, list):
                behaviors_to_display = behavior_data
            elif isinstance(behavior_data, dict):
                # Convert dictionary to list format
                for trait, data in behavior_data.items():
                    if isinstance(data, dict):
                        behavior = {
                            "behavior": data.get("label", trait),
                            "confidence": data.get("confidence", 0.7),
                            "reasoning": data.get("description", ""),
                        }
                        behaviors_to_display.append(behavior)

            for behavior in behaviors_to_display:
                behavior_frame = ttk.Frame(behaviors_frame)
                behavior_frame.pack(fill=tk.X, pady=5)

                # Get behavior name from various possible fields
                behavior_name = behavior.get("behavior", "")
                if not behavior_name and "label" in behavior:
                    behavior_name = behavior["label"]

                if behavior_name:
                    behavior_label = ttk.Label(
                        behavior_frame,
                        text=behavior_name,
                        font=("Helvetica", 11, "bold"),
                    )
                    behavior_label.pack(anchor=tk.W)

                    # Get confidence value
                    confidence = 0.7  # Default
                    if "confidence" in behavior:
                        confidence = behavior["confidence"]
                    elif "score" in behavior:
                        confidence = behavior["score"]

                    conf_frame = ttk.Frame(behavior_frame)
                    conf_frame.pack(fill=tk.X, pady=2)

                    conf_label = ttk.Label(
                        conf_frame, text="Confidence: ", width=12, anchor=tk.W
                    )
                    conf_label.pack(side=tk.LEFT)

                    conf_bar = ttk.Progressbar(
                        conf_frame, value=int(confidence * 100), length=100
                    )
                    conf_bar.pack(side=tk.LEFT, padx=5)

                    conf_value = ttk.Label(conf_frame, text=f"{confidence:.0%}")
                    conf_value.pack(side=tk.LEFT)

                    # Display reasoning if available
                    if "reasoning" in behavior:
                        reason_label = ttk.Label(
                            behavior_frame,
                            text=f"Reasoning: {behavior['reasoning']}",
                            wraplength=350,
                        )
                        reason_label.pack(anchor=tk.W, pady=2)
                    elif "description" in behavior:
                        reason_label = ttk.Label(
                            behavior_frame,
                            text=behavior["description"],
                            wraplength=350,
                        )
                        reason_label.pack(anchor=tk.W, pady=2)
        else:
            # If no behavior data is available
            no_behaviors = ttk.Label(
                behaviors_frame,
                text="No behavior predictions available",
                wraplength=350,
            )
            no_behaviors.pack(pady=20)

    def _create_mock_predictions(self):
        """Create mock prediction data for the predictions tab when no real data is available"""
        # Clear existing widgets
        for widget in self.predictions_frame.winfo_children():
            widget.destroy()

        # Main container with scrolling
        canvas = tk.Canvas(self.predictions_frame)
        scrollbar = ttk.Scrollbar(
            self.predictions_frame, orient="vertical", command=canvas.yview
        )
        main_frame = ttk.Frame(canvas, padding=20)

        # Configure scroll behavior
        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Allow canvas to expand and fill the predictions frame
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title and intro
        title = ttk.Label(
            main_frame, text="Profile Predictions", style="TitleLabel.TLabel"
        )
        title.pack(pady=20)

        disclaimer = ttk.Frame(main_frame, padding=10)
        disclaimer.pack(fill=tk.X, pady=10)

        warning_icon = ttk.Label(disclaimer, text="ℹ️", font=("Arial", 20))
        warning_icon.pack(side=tk.LEFT, padx=10)

        disclaimer_text = ttk.Label(
            disclaimer,
            text="This tab shows sample prediction data. Run an actual profile analysis to see real predictions.",
            wraplength=600,
            foreground=self.colors["info"],
        )
        disclaimer_text.pack(fill=tk.X, expand=True, padx=10)

        description = ttk.Label(
            main_frame,
            text="Based on profile analysis, the system predicts the following patterns and interests.",
            wraplength=700,
        )
        description.pack(pady=10)

        # Create a two-column layout for predictions
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left column - Interests
        interests_frame = ttk.LabelFrame(
            columns_frame, text="Predicted Interests", padding=10
        )
        interests_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Sample interest data
        sample_interests = [
            {
                "interest": "Environmental Sustainability",
                "confidence": 0.85,
                "reasoning": "Based on engagement with climate content and sustainability topics",
            },
            {
                "interest": "Technology Innovation",
                "confidence": 0.78,
                "reasoning": "Frequent discussion of emerging tech trends and new products",
            },
            {
                "interest": "Outdoor Activities",
                "confidence": 0.65,
                "reasoning": "Mentions of hiking, camping, and nature photography",
            },
        ]

        for interest in sample_interests:
            interest_frame = ttk.Frame(interests_frame)
            interest_frame.pack(fill=tk.X, pady=5)

            interest_label = ttk.Label(
                interest_frame,
                text=interest["interest"],
                font=("Helvetica", 11, "bold"),
            )
            interest_label.pack(anchor=tk.W)

            conf_frame = ttk.Frame(interest_frame)
            conf_frame.pack(fill=tk.X, pady=2)

            conf_label = ttk.Label(
                conf_frame, text="Confidence: ", width=12, anchor=tk.W
            )
            conf_label.pack(side=tk.LEFT)

            conf_bar = ttk.Progressbar(
                conf_frame, value=int(interest["confidence"] * 100), length=100
            )
            conf_bar.pack(side=tk.LEFT, padx=5)

            conf_value = ttk.Label(conf_frame, text=f"{interest['confidence']:.0%}")
            conf_value.pack(side=tk.LEFT)

            reason_label = ttk.Label(
                interest_frame,
                text=f"Reasoning: {interest['reasoning']}",
                wraplength=350,
            )
            reason_label.pack(anchor=tk.W, pady=2)

        # Right column - Behaviors
        behaviors_frame = ttk.LabelFrame(
            columns_frame, text="Predicted Behaviors", padding=10
        )
        behaviors_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Sample behavior data
        sample_behaviors = [
            {
                "behavior": "Increased Social Networking",
                "confidence": 0.72,
                "reasoning": "Growing pattern of engagement and networking activities",
            },
            {
                "behavior": "Content Creation Focus",
                "confidence": 0.83,
                "reasoning": "Trend toward creating and sharing original content",
            },
            {
                "behavior": "Community Leadership",
                "confidence": 0.61,
                "reasoning": "Emerging pattern of organizing discussions and events",
            },
        ]

        for behavior in sample_behaviors:
            behavior_frame = ttk.Frame(behaviors_frame)
            behavior_frame.pack(fill=tk.X, pady=5)

            behavior_label = ttk.Label(
                behavior_frame,
                text=behavior["behavior"],
                font=("Helvetica", 11, "bold"),
            )
            behavior_label.pack(anchor=tk.W)

            conf_frame = ttk.Frame(behavior_frame)
            conf_frame.pack(fill=tk.X, pady=2)

            conf_label = ttk.Label(
                conf_frame, text="Confidence: ", width=12, anchor=tk.W
            )
            conf_label.pack(side=tk.LEFT)

            conf_bar = ttk.Progressbar(
                conf_frame, value=int(behavior["confidence"] * 100), length=100
            )
            conf_bar.pack(side=tk.LEFT, padx=5)

            conf_value = ttk.Label(conf_frame, text=f"{behavior['confidence']:.0%}")
            conf_value.pack(side=tk.LEFT)

            reason_label = ttk.Label(
                behavior_frame,
                text=f"Reasoning: {behavior['reasoning']}",
                wraplength=350,
            )
            reason_label.pack(anchor=tk.W, pady=2)

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
        self.analysis_thread = threading.Thread(
            target=self._run_analysis, args=(platform, profile_id)
        )
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
            # Use root reference to avoid AttributeError
            self.after(1000, lambda: self._show_results())
        except Exception as e:
            # Handle errors
            self.progress_status_var.set(f"Error: {str(e)}")
            print(f"Analysis error: {str(e)}")

            # Fix the attribute error by using a proper lambda
            # Schedule reset_form with proper context
            self.after(1000, self._reset_form)

    def _reset_form(self):
        """Reset the form after an error"""
        # Hide progress frame
        self.progress_frame.pack_forget()

        # Reset the input frame to its initial state
        self._reset_input_frame()

        # Clear any partial results
        self.analysis_results = None

        # Update status
        self.status_var.set("Ready to start new analysis")

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
        self.status_var.set(
            f"Analysis completed for {self.profile_var.get()} on {self.platform_var.get()}"
        )

        # Offer to save
        save = messagebox.askyesno(
            "Analysis Complete",
            "Analysis has been completed. Would you like to save the results?",
        )
        if save:
            self._save_results()

        # Offer to iterate through tabs
        iterate = messagebox.askyesno(
            "View Results",
            "Do you want to automatically iterate through all result tabs?",
        )
        if iterate:
            self.iterate_tabs()

    def iterate_tabs(self, current_tab=1, delay=3000):
        """Iterate through result tabs with a delay between each tab

        Args:
            current_tab: The index of the current tab (default: 1, which is the Summary tab)
            delay: The delay in milliseconds before switching to the next tab
        """
        # Skip the input tab (index 0)
        if current_tab == 0:
            current_tab = 1

        # Switch to the current tab
        self.notebook.select(current_tab)

        # Schedule the next tab switch if not at the last tab
        if current_tab < self.notebook.index("end") - 1:
            self.after(delay, lambda: self.iterate_tabs(current_tab + 1, delay))
        else:
            # When we reach the last tab, offer to loop back to the summary tab
            self.after(delay, lambda: self._ask_continue_iteration())

    def _ask_continue_iteration(self):
        """Ask if the user wants to continue tab iteration"""
        continue_iteration = messagebox.askyesno(
            "Continue to iterate?",
            "Do you want to continue viewing all tabs from the beginning?",
        )
        if continue_iteration:
            self.iterate_tabs(1)  # Start from Summary tab (index 1)

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
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )

        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
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

        file_types = [
            ("HTML Report", "*.html"),
            ("JSON File", "*.json"),
            ("All Files", "*.*"),
        ]

        file_path = filedialog.asksaveasfilename(
            title="Save Analysis Results",
            defaultextension=".html",
            filetypes=file_types,
        )

        if not file_path:
            return

        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".json":
                # Save as JSON
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.analysis_results, f, indent=2)
            else:
                # Save as HTML
                html_content = self._generate_html_report()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

            self.status_var.set(f"Results saved to {os.path.basename(file_path)}")
            messagebox.showinfo("Save Complete", f"Results saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving results: {str(e)}")

    def _generate_html_report(self):
        """Generate an HTML report from the analysis results"""
        metadata = self.analysis_results.get("metadata", {})
        content = self.analysis_results.get("content_analysis", {})
        authenticity = self.analysis_results.get("authenticity_analysis", {})
        predictions = self.analysis_results.get("predictions", {})

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Profile Analysis Report - {metadata.get('profile_id', '')}</title>
    <meta charset="utf-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1, h2, h3 {{ color: #2c3e50; margin-top: 1.5em; }}
        .section {{ margin-bottom: 30px; border: 1px solid #eee; padding: 20px; border-radius: 5px; }}
        .metadata {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
        .score {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .trait {{ margin: 10px 0; }}
        .progress-bar {{ 
            background-color: #e9ecef; 
            height: 20px; 
            border-radius: 10px; 
            overflow: hidden; 
            margin: 5px 0;
        }}
        .progress-fill {{ 
            height: 100%; 
            background-color: #4a6fa5; 
            transition: width 0.3s ease; 
        }}
        .chart-container {{
            position: relative;
            margin: 20px 0;
            height: 300px;
        }}
        .timeline-item {{
            margin-bottom: 15px;
            padding-left: 20px;
            border-left: 2px solid #4a6fa5;
        }}
        .timeline-date {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        .risk-low {{ background-color: #28a745; }}
        .risk-medium {{ background-color: #ffc107; }}
        .risk-high {{ background-color: #dc3545; }}
        .metric-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <h1>Profile Analysis Report</h1>
    
    <div class="section metadata">
        <h2>Analysis Information</h2>
        <p><strong>Profile ID:</strong> {metadata.get('profile_id', '')}</p>
        <p><strong>Platform:</strong> {metadata.get('platform', '').title()}</p>
        <p><strong>Analysis Date:</strong> {metadata.get('analysis_date', '')}</p>
        <p><strong>Analyzer Version:</strong> {metadata.get('analyzer_version', '')}</p>
    </div>"""

        # Summary section
        if "summary" in content:
            html += """
    <div class="section">
        <h2>Analysis Summary</h2>"""
            summary = content["summary"]
            for key, value in summary.items():
                html += f"""
        <div class="metric-card">
            <h3>{key.replace('_', ' ').title()}</h3>
            <p class="metric-value">{value}</p>
        </div>"""
            html += "\n    </div>"

        # Timeline section
        if "timeline" in content:
            html += """
    <div class="section">
        <h2>Activity Timeline</h2>
        <div class="timeline">"""

            for event in content["timeline"]:
                event_date = event.get("date", "")
                event_type = event.get("type", "").title()
                event_desc = event.get("description", "")
                html += f"""
            <div class="timeline-item">
                <div class="timeline-date">{event_date}</div>
                <strong>{event_type}</strong>
                <p>{event_desc}</p>
            </div>"""
            html += "\n        </div>\n    </div>"

        # Personality traits section
        if "personality_traits" in content:
            html += """
    <div class="section">
        <h2>Personality Traits & Interests</h2>
        <div class="chart-container">
            <canvas id="traitsChart"></canvas>
        </div>"""

            # Add traits data for the chart
            traits = content["personality_traits"]
            html += f"""
        <script>
            new Chart(document.getElementById('traitsChart').getContext('2d'), {{
                type: 'radar',
                data: {{
                    labels: {list(traits.keys())},
                    datasets: [{{
                        label: 'Personality Traits',
                        data: {list(traits.values())},
                        backgroundColor: 'rgba(74, 111, 165, 0.2)',
                        borderColor: 'rgb(74, 111, 165)',
                        pointBackgroundColor: 'rgb(74, 111, 165)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(74, 111, 165)'
                    }}]
                }},
                options: {{
                    scales: {{
                        r: {{
                            beginAtZero: true,
                            max: 1
                        }}
                    }}
                }}
            }});
        </script>"""

        # Writing Style section
        if "writing_style" in content:
            html += """
    <div class="section">
        <h2>Writing Style Analysis</h2>"""

            writing = content["writing_style"]
            metrics = {
                "complexity": "Text Complexity",
                "formality": "Formality Level",
                "emotional_tone": "Emotional Expression",
                "vocabulary_diversity": "Vocabulary Range",
            }

            for key, label in metrics.items():
                if key in writing:
                    value = writing[key]
                    percentage = int(value * 100)
                    html += f"""
        <div class="trait">
            <div><strong>{label}</strong> ({percentage}%)</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {percentage}%"></div>
            </div>
        </div>"""

            if "word_patterns" in writing:
                html += """
        <div class="mt-4">
            <h3>Common Word Patterns</h3>
            <ul>"""
                for pattern in writing["word_patterns"]:
                    html += f"\n                <li>{pattern}</li>"
                html += "\n            </ul>\n        </div>"

        # Authenticity section
        if "overall_authenticity" in authenticity:
            auth = authenticity["overall_authenticity"]
            score = int(auth.get("score", 0) * 100)
            html += f"""
    <div class="section">
        <h2>Authenticity Analysis</h2>
        <div class="chart-container">
            <canvas id="authenticityChart"></canvas>
        </div>
        <div class="score">Overall Score: {score}%</div>
        <p><strong>Confidence:</strong> {int(auth.get("confidence", 0) * 100)}%</p>"""

            html += (
                """
        <script>
            new Chart(document.getElementById('authenticityChart').getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Authentic', 'Risk'],
                    datasets: [{
                        data: ["""
                + f"{score}, {100-score}"
                + """],
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.2)',
                            'rgba(220, 53, 69, 0.2)'
                        ],
                        borderColor: [
                            'rgb(40, 167, 69)',
                            'rgb(220, 53, 69)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    cutout: '70%'
                }
            });
        </script>"""
            )

            if "potential_issues" in auth and auth["potential_issues"]:
                html += """
        <div class="mt-4">
            <h3>Potential Issues</h3>
            <ul>"""
                for issue in auth["potential_issues"]:
                    html += f"\n                <li>{issue}</li>"
                html += "\n            </ul>\n        </div>"
            html += "\n    </div>"

        # Predictions section
        if predictions:
            html += """
    <div class="section">
        <h2>Predictions & Future Insights</h2>"""

            # Future interests
            if "future_interests" in predictions:
                html += """
        <h3>Predicted Future Interests</h3>
        <div class="row">"""
                for interest in predictions["future_interests"]:
                    confidence = int(interest.get("confidence", 0) * 100)
                    html += f"""
            <div class="col-md-6 mb-3">
                <div class="metric-card">
                    <h4>{interest["interest"]}</h4>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {confidence}%"></div>
                    </div>
                    <p class="mt-2">Confidence: {confidence}%</p>
                    {f'<p>{interest["reasoning"]}</p>' if "reasoning" in interest else ''}
                </div>
            </div>"""
                html += "\n        </div>"

            # Behavioral predictions
            if "behavioral_predictions" in predictions:
                html += """
        <h3>Behavioral Predictions</h3>
        <div class="chart-container">
            <canvas id="behaviorChart"></canvas>
        </div>"""

                behaviors = predictions["behavioral_predictions"]
                html += f"""
        <script>
            new Chart(document.getElementById('behaviorChart').getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: {[b["behavior"] for b in behaviors]},
                    datasets: [{{
                        label: 'Likelihood',
                        data: {[b["probability"] for b in behaviors]},
                        backgroundColor: 'rgba(74, 111, 165, 0.2)',
                        borderColor: 'rgb(74, 111, 165)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 1
                        }}
                    }}
                }}
            }});
        </script>"""

        html += """
    <div class="section">
        <p><em>This report was generated by ProfileScope. The analysis is based on publicly available data 
        and should be considered as insights rather than definitive conclusions.</em></p>
    </div>
    </body>
    </html>"""

        return html

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
        ProfileScope: Social Media Profile Analyzer
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

        messagebox.showinfo("About ProfileScope", about_text)


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



def main():
    """Main function to run the desktop application"""
    try:
        print("🖥️  Initializing ProfileScope Desktop Application...")
        
        # Check system compatibility
        if not check_macos_compatibility():
            print("❌ System compatibility check failed")
            return 1
            
        # Create and run the application
        app = AnalyzerApp()
        print("✅ Application initialized successfully")
        app.mainloop()
        return 0
        
    except Exception as e:
        print(f"❌ Fatal error starting desktop application: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
