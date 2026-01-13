# beamer_ide.py - Enhanced with advanced media handling
import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import re
import json
import fitz  # PyMuPDF
import platform
from PIL import Image, ImageDraw, ImageSequence
from PIL.ImageQt import ImageQt
import numpy as np
import urllib.request
import hashlib
from urllib.parse import urlparse
import webbrowser
from pytube import YouTube
import validators
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTextEdit, QListWidget, QVBoxLayout,
    QWidget, QPushButton, QFileDialog, QLabel, QHBoxLayout, QMessageBox,
    QMenuBar, QMenu, QAction, QInputDialog, QFileSystemModel, QTreeView,
    QTabWidget, QDockWidget, QToolBar, QComboBox, QLineEdit, QDesktopWidget,
    QDialog, QDialogButtonBox
)
from PyQt5.QtGui import (
    QTextCursor, QFont, QSyntaxHighlighter, QTextCharFormat, QColor,
    QPixmap, QPalette, QImage
)
from PyQt5.QtCore import Qt, QTimer, QDir, QRect, QUrl
from PyQt5.QtGui import QDesktopServices

#----------------------------
# Handle unicode
#----------------------------
UNICODE_TO_LATEX = {
    '₂': r'_{2}',  # Changed from \textsubscript to math mode
    '²': r'^2',
    '₃': r'_{3}',
    '³': r'^3',
    '→': r'\rightarrow',
    '←': r'\leftarrow',
    '±': r'\pm',
    '×': r'\times',
    '÷': r'\div',
    'α': r'\alpha',
    'β': r'\beta',
    'γ': r'\gamma',
    'δ': r'\delta',
    'ε': r'\epsilon',
    'θ': r'\theta',
    'λ': r'\lambda',
    'μ': r'\mu',
    'π': r'\pi',
    'σ': r'\sigma',
    'φ': r'\phi',
    'ω': r'\omega',
    '≤': r'\leq',
    '≥': r'\geq',
    '≠': r'\neq',
    '≈': r'\approx',
    '∞': r'\infty',
    '∂': r'\partial',
    '∇': r'\nabla',
    '√': r'\sqrt{}',
    '∑': r'\sum',
    '∏': r'\prod',
    '∫': r'\int',
    'ℕ': r'\mathbb{N}',
    'ℤ': r'\mathbb{Z}',
    'ℚ': r'\mathbb{Q}',
    'ℝ': r'\mathbb{R}',
    'ℂ': r'\mathbb{C}',
    '∈': r'\in',
    '∉': r'\notin',
    '⊆': r'\subseteq',
    '⊂': r'\subset',
    '∪': r'\cup',
    '∩': r'\cap',
    '∅': r'\emptyset'
}

def convert_unicode_to_latex(text: str) -> str:
    """Convert Unicode characters to LaTeX equivalents with math mode awareness"""
    # Define the subscript zero character separately
    subscript_zero = '\u2080'

    # First handle superscripts/subscripts that should be in math mode
    text = re.sub(r'([\u2070-\u2079\u2080-\u2089])',
                 lambda m: '_{{{}}}'.format(
                     ''.join(str(ord(c) - ord(subscript_zero))
                     for c in m.group(1)
                 )),
                 text)

    # Then handle other special characters
    for char, latex_cmd in UNICODE_TO_LATEX.items():
        text = text.replace(char, latex_cmd)

    return text

def process_math_mode_segments(text):
    """Process text segments, handling math mode separately"""
    segments = re.split(r'(\$.*?\$|\\\(.*?\\\)|\\\[.*?\\\])', text)
    processed = []

    for segment in segments:
        if segment.startswith('$') or segment.startswith(r'\(') or segment.startswith(r'\['):
            # Inside math mode - just convert Unicode
            processed.append(convert_unicode_to_latex(segment))
        else:
            # Outside math mode - convert Unicode and escape special chars
            processed.append(escape_latex_special_chars(convert_unicode_to_latex(segment)))

    return ''.join(processed)

#------------------------------
# Handle escape chars
#------------------------------

def escape_latex_special_chars(text: str) -> str:
    """Escape special LaTeX characters outside of tables/math mode"""
    # First handle ampersands - only escape if not in table context
    if '\\begin{tabular}' not in text and '\\begin{array}' not in text:
        text = text.replace('&', r'\&')

    # Escape other special characters
    replacements = {
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
        '|': r'\textbar{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}'
    }

    for char, escaped in replacements.items():
        text = text.replace(char, escaped)

    return text


# --------------------------
# Built-in Preamble Template
# --------------------------
DEFAULT_PREAMBLE = r"""\documentclass[aspectratio=169]{beamer}

% Essential packages (core)
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{xstring}
\usepackage{animate}
\usepackage{multimedia}
\usepackage{xifthen}
\usepackage{xcolor}

% Define the style for covered text
\setbeamercovered{dynamic}
\setbeamerfont{item projected}{size=\small}
\setbeamercolor{alerted text}{fg=white}

% Extended packages with fallbacks
\IfFileExists{tcolorbox.sty}{\usepackage{tcolorbox}}{}
\IfFileExists{fontawesome5.sty}{\usepackage{fontawesome5}}{}
\IfFileExists{pifont.sty}{\usepackage{pifont}}{}
\IfFileExists{soul.sty}{\usepackage{soul}}{}

% Package configurations
\pgfplotsset{compat=1.18}
\usetikzlibrary{shadows.blur, shapes.geometric, positioning, arrows.meta, backgrounds, fit}

% Custom text effects
\newcommand{\shadowtext}[2][2pt]{%
   \begin{tikzpicture}[baseline]
       \node[blur shadow={shadow blur steps=5,shadow xshift=0pt,shadow yshift=-#1,
             shadow opacity=0.75}, text=white] {#2};
   \end{tikzpicture}%
}

\newcommand{\glowtext}[2][myblue]{%
   \begin{tikzpicture}[baseline]
       \node[circle, inner sep=1pt,
             blur shadow={shadow blur steps=10,shadow xshift=0pt,
             shadow yshift=0pt,shadow blur radius=5pt,
             shadow opacity=0.5,shadow color=#1},
             text=white] {#2};
   \end{tikzpicture}%
}

% Color definitions
\definecolor{myred}{RGB}{255,50,50}
\definecolor{myblue}{RGB}{0,130,255}
\definecolor{mygreen}{RGB}{0,200,100}
\definecolor{myyellow}{RGB}{255,210,0}
\definecolor{myorange}{RGB}{255,130,0}
\definecolor{mypurple}{RGB}{147,112,219}
\definecolor{mypink}{RGB}{255,105,180}
\definecolor{myteal}{RGB}{0,128,128}

% Glow colors
\definecolor{glowblue}{RGB}{0,150,255}
\definecolor{glowyellow}{RGB}{255,223,0}
\definecolor{glowgreen}{RGB}{0,255,128}
\definecolor{glowpink}{RGB}{255,182,193}

% Highlighting commands
\newcommand{\hlbias}[1]{\textcolor{myblue}{\textbf{#1}}}
\newcommand{\hlvariance}[1]{\textcolor{mypink}{\textbf{#1}}}
\newcommand{\hltotal}[1]{\textcolor{myyellow}{\textbf{#1}}}
\newcommand{\hlkey}[1]{\colorbox{myblue!20}{\textcolor{white}{\textbf{#1}}}}
\newcommand{\hlnote}[1]{\colorbox{mygreen!20}{\textcolor{white}{\textbf{#1}}}}

% Theme setup
\usetheme{Madrid}
\usecolortheme{owl}

% Color settings
\setbeamercolor{normal text}{fg=white}
\setbeamercolor{structure}{fg=myyellow}
\setbeamercolor{alerted text}{fg=myorange}
\setbeamercolor{example text}{fg=mygreen}
\setbeamercolor{background canvas}{bg=black}
\setbeamercolor{frametitle}{fg=white,bg=black}

% Notes support
\usepackage{pgfpages}
\setbeameroption{show notes on second screen=right}
\setbeamertemplate{note page}{\pagecolor{yellow!5}\insertnote}

% Progress bar setup
\makeatletter
\def\progressbar@progressbar{}
\newcount\progressbar@tmpcounta
\newcount\progressbar@tmpcountb
\newdimen\progressbar@pbht
\newdimen\progressbar@pbwd
\newdimen\progressbar@tmpdim

\progressbar@pbwd=\paperwidth
\progressbar@pbht=1pt

\def\progressbar@progressbar{%
   \begin{tikzpicture}[very thin]
       \shade[top color=myblue!50,bottom color=myblue]
           (0pt, 0pt) rectangle (\insertframenumber\progressbar@pbwd/\inserttotalframenumber, \progressbar@pbht);
   \end{tikzpicture}%
}

% Frame title template
\setbeamertemplate{frametitle}{
   \nointerlineskip
   \vskip1ex
   \begin{beamercolorbox}[wd=\paperwidth,ht=4ex,dp=2ex]{frametitle}
       \begin{minipage}[t]{\dimexpr\paperwidth-4em}
           \centering
           \vspace{2pt}
           \insertframetitle
           \vspace{2pt}
       \end{minipage}
   \end{beamercolorbox}
   \vskip.5ex
   \progressbar@progressbar
}

% Footline template
\setbeamertemplate{footline}{%
 \leavevmode%
 \hbox{%
   \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{author in head/foot}%
     \usebeamerfont{author in head/foot}\insertshortauthor~(\insertshortinstitute)%
   \end{beamercolorbox}%
   \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{title in head/foot}%
     \usebeamerfont{title in head/foot}\insertshorttitle%
   \end{beamercolorbox}%
   \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,right]{date in head/foot}%
     \usebeamerfont{date in head/foot}\insertshortdate{}\hspace*{2em}%
     \insertframenumber{} / \inserttotalframenumber\hspace*{2ex}%
   \end{beamercolorbox}}%
 \vskip0pt%
}

% Additional settings
\setbeamersize{text margin left=5pt,text margin right=5pt}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{blocks}[rounded][shadow=true]

% Default title info (user can change these)
\title{Advances in Solid State Hydrogen using AI}
\subtitle{Path to Net-Zero}
\author{Ninan Sajeeth Philip}
\institute{\textcolor{mygreen}{Artificial Intelligent Research and Intelligent Systems}}
\date{\today}

\begin{document}
"""

DEFAULT_SLIDE = r"""\title{Slide Title}
\begin{Content}
\begin{itemize}
\item First item
\item Second item
\end{itemize}
\end{Content}

\begin{Notes}
Speaker notes here
\end{Notes}
"""
#----------------------------------------------
#Enhanced Preamble Handling
#---------------------------------------------
def ensure_pgfplots_compat(preamble: str) -> str:
    """Ensure pgfplots compatibility mode is set"""
    if r'\usepackage{pgfplots}' in preamble and r'\pgfplotsset{compat=' not in preamble:
        preamble = preamble.replace(
            r'\usepackage{pgfplots}',
            r'\usepackage{pgfplots}' + '\n' + r'\pgfplotsset{compat=1.18}'
        )
    return preamble

# --------------------------
# Config Class
# --------------------------
class Config:
    _instance = None

    def __init__(self):
        self.settings = {
            'syntax_highlighting': True,
            'auto_save': True,
            'theme': 'dark',
            'font_size': 12,
            'recent_files': [],
            'default_preamble': DEFAULT_PREAMBLE,
            'working_directory': str(Path.home())
        }
        self._config_path = self._get_config_path()
        self._load_config()

    @classmethod
    def load(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_config_path(self) -> Path:
        home = Path.home()
        if sys.platform == 'win32':
            return home / 'AppData' / 'Local' / 'beamer_ide' / 'config.json'
        else:
            return home / '.config' / 'beamer_ide' / 'config.json'

    def _load_config(self):
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            if self._config_path.exists():
                with open(self._config_path, 'r') as f:
                    loaded = json.load(f)
                    for key in loaded:
                        if key in self.settings:
                            self.settings[key] = loaded[key]
        except Exception:
            self._reset_defaults()

    def save_config(self):
        try:
            with open(self._config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _reset_defaults(self):
        self.settings = {
            'syntax_highlighting': True,
            'auto_save': True,
            'theme': 'dark',
            'font_size': 12,
            'recent_files': [],
            'default_preamble': DEFAULT_PREAMBLE,
            'working_directory': str(Path.home())
        }


class MediaDownloadDialog(QDialog):
    """Dialog for adding media from URLs or searching online"""
    def __init__(self, parent=None, slide_title=""):
        super().__init__(parent)
        self.setWindowTitle("Add Media from Web")
        self.slide_title = slide_title

        layout = QVBoxLayout()

        # URL Input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter image/video URL (YouTube, etc.)")
        layout.addWidget(QLabel("Media URL:"))
        layout.addWidget(self.url_input)

        # Search Button
        self.search_btn = QPushButton(f"Search scientific images about: '{slide_title}'")
        self.search_btn.clicked.connect(self.search_images)
        layout.addWidget(self.search_btn)

        # Local file button
        self.local_btn = QPushButton("Browse Local File...")
        self.local_btn.clicked.connect(self.browse_local)
        layout.addWidget(self.local_btn)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def search_images(self):
        """Open browser with scientific image search"""
        query = (f"scientific presentation image {self.slide_title} "
                 "site:unsplash.com OR site:pexels.com OR site:flickr.com")
        webbrowser.open(f"https://www.google.com/search?q={query}&tbm=isch&tbs=sur:fmc")

    def browse_local(self):
        """Open file dialog for local files"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Media File",
            "",
            "Media Files (*.png *.jpg *.jpeg *.gif *.mp4 *.avi *.mov);;All Files (*)"
        )
        if file_path:
            self.url_input.setText(file_path)

# --------------------------
# Presentation Classes
# --------------------------
@dataclass
class Slide:
    title: str
    content: List[str]
    notes: List[str]
    media: Optional[str] = None

class PresentationManager:
    def __init__(self, write_terminal_callback=None):  # Add callback parameter
        self.slides: List[Slide] = []
        self.current_slide_index = 0
        self.preamble = ensure_pgfplots_compat(DEFAULT_PREAMBLE)
        self.postamble = r"\end{document}"
        self.is_text_file = False
        self.original_content = ""
        self.converted_tex = ""
        self.current_file = ""
        self.title_info = {
            'title': "Untitled Presentation",
            'subtitle': "",
            'author': "",
            'institute': "",
            'date': r"\today",
            'logo': ""
        }
        self.write_terminal = write_terminal_callback  # Store callback


    def fetch_media(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Download and cache media from URL with proper error handling"""
        try:
            base_dir = Path(self.current_file).parent if self.current_file else Path.cwd()
            media_dir = base_dir / "media"
            media_dir.mkdir(exist_ok=True)

            if self.write_terminal:
                self.write_terminal(f"Processing media: {url}", "blue")

            # YouTube handling
            if "youtube.com" in url or "youtu.be" in url:
                try:
                    yt = YouTube(url)
                    stream = yt.streams.filter(
                        progressive=True,
                        file_extension='mp4'
                    ).order_by('resolution').desc().first()

                    if not stream:
                        if self.write_terminal:
                            self.write_terminal("No suitable YouTube stream found", "orange")
                        return None, None

                    filename = f"{yt.video_id}.mp4"
                    local_path = media_dir / filename

                    if not local_path.exists():
                        if self.write_terminal:
                            self.write_terminal(f"Downloading YouTube video: {yt.title}", "blue")
                        stream.download(output_path=str(media_dir), filename=filename)

                    return str(local_path), f"Video: {yt.title} (\\url{{{url}}})"
                except Exception as e:
                    if self.write_terminal:
                        self.write_terminal(f"YouTube download error: {str(e)}", "red")
                    return None, None

            # Regular URL handling
            elif validators.url(url):
                parsed = urlparse(url)
                original_filename = Path(parsed.path).name

                # Clean filename (remove query strings and special characters)
                clean_name = re.sub(r'[^\w\-_. ]', '_', original_filename)
                if not clean_name:
                    clean_name = "downloaded_media"

                # Ensure we have a proper extension
                ext = Path(clean_name).suffix.lower()
                if not ext:
                    if any(x in parsed.netloc for x in ['imgur', 'flickr', 'unsplash']):
                        ext = '.jpg'
                    else:
                        # Try to determine extension from content type if possible
                        try:
                            with urllib.request.urlopen(url) as response:
                                content_type = response.info().get_content_type()
                                if content_type == 'image/jpeg':
                                    ext = '.jpg'
                                elif content_type == 'image/png':
                                    ext = '.png'
                                elif content_type == 'image/gif':
                                    ext = '.gif'
                                else:
                                    ext = '.bin'
                        except:
                            ext = '.bin'

                    clean_name = clean_name + ext

                local_path = media_dir / clean_name

                if not local_path.exists():
                    try:
                        urllib.request.urlretrieve(url, local_path)
                        if self.write_terminal:
                            self.write_terminal(f"Downloaded media: {clean_name}", "green")
                    except Exception as e:
                        if self.write_terminal:
                            self.write_terminal(f"Failed to download media: {str(e)}", "red")
                        return None, None

                # Generate appropriate citation with \url{}
                source = parsed.netloc.replace('www.', '')
                if 'unsplash' in source:
                    return str(local_path), f"Photo from Unsplash (\\url{{{url}}})"
                elif 'pexels' in source:
                    return str(local_path), f"Photo from Pexels (\\url{{{url}}})"
                else:
                    return str(local_path), f"Source: \\url{{{url}}}"

            # Local file handling
            else:
                # Check if local file exists
                local_path = Path(url)
                if not local_path.exists():
                    if self.write_terminal:
                        self.write_terminal(f"Local file not found: {url}", "red")
                    return None, None
                return url, f"Local file: {Path(url).name}"

        except Exception as e:
            if self.write_terminal:
                self.write_terminal(f"Media processing error: {str(e)}", "red")
            return None, None

    def browse_media(self):
        """Enhanced media browser with URL, search and local file support"""
        if not self.slides or self.current_slide_index < 0:
            return

        slide_title = self.slides[self.current_slide_index].title
        dialog = MediaDownloadDialog(self, slide_title)

        if dialog.exec_() == QDialog.Accepted and dialog.url_input.text():
            media_url = dialog.url_input.text()
            local_path, citation = self.fetch_media(media_url)

            if local_path:
                # Update UI
                self.graphics_path.setText(media_url)
                self.update_media_preview(local_path)

                # Add citation to notes if needed
                if citation and citation not in self.notes_editor.toPlainText():
                    current_notes = self.notes_editor.toPlainText()
                    self.notes_editor.setPlainText(
                        f"{current_notes}\nMedia Citation: {citation}".strip()
                    )


    def add_slide(self, position=None):
        new_slide = Slide(
            title="New Slide",
            content=["\\begin{itemize}", "\\item Item 1", "\\end{itemize}"],
            notes=["Speaker notes here"]
        )
        if position is None:
            self.slides.append(new_slide)
        else:
            self.slides.insert(position, new_slide)
        return new_slide

    def load_file(self, file_path):
        self.current_file = file_path
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.is_text_file = path.suffix.lower() == '.txt'

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.original_content = content

        if self.is_text_file:
            self._parse_text_file(content)
        else:
            self._parse_latex_file(content)

        # Initialize current slide index
        self.current_slide_index = 0 if self.slides else -1

    def _parse_text_file(self, content):
        """Parse simplified text format into slides"""
        self.slides = []
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # Extract title info if present
        title_slide = self._extract_title_slide(lines)
        if title_slide:
            self.title_info = title_slide
            # Remove title info lines
            lines = lines[len(title_slide['raw_lines']):] if 'raw_lines' in title_slide else lines

        current_slide = None
        in_notes = False

        for line in lines:
            if line.startswith('# '):
                if current_slide:
                    self.slides.append(current_slide)
                title = line[2:].strip()
                current_slide = Slide(title=title, content=[], notes=[], media=None)
                in_notes = False
            elif line.startswith('@media:'):
                if current_slide:
                    current_slide.media = line[6:].strip()
            elif line == 'NOTES:':
                in_notes = True
            elif current_slide:
                if in_notes:
                    current_slide.notes.append(line)
                else:
                    current_slide.content.append(line)

        if current_slide:
            self.slides.append(current_slide)

        # Generate LaTeX version
        self.converted_tex = self._generate_latex_from_slides()

    def _extract_title_slide(self, lines):
        """Extract title slide info if present"""
        if not lines or not lines[0].startswith('% Title:'):
            return None

        title_info = {
            'title': lines[0].replace('% Title:', '').strip(),
            'subtitle': '',
            'author': '',
            'institute': '',
            'date': r"\today",
            'logo': '',
            'raw_lines': [lines[0]]
        }

        for line in lines[1:]:
            if line.startswith('% Subtitle:'):
                title_info['subtitle'] = line.replace('% Subtitle:', '').strip()
                title_info['raw_lines'].append(line)
            elif line.startswith('% Author:'):
                title_info['author'] = line.replace('% Author:', '').strip()
                title_info['raw_lines'].append(line)
            elif line.startswith('% Institute:'):
                title_info['institute'] = line.replace('% Institute:', '').strip()
                title_info['raw_lines'].append(line)
            elif line.startswith('% Date:'):
                title_info['date'] = line.replace('% Date:', '').strip()
                title_info['raw_lines'].append(line)
            elif line.startswith('% Logo:'):
                title_info['logo'] = line.replace('% Logo:', '').strip()
                title_info['raw_lines'].append(line)
            else:
                break

        return title_info

    def _parse_latex_file(self, content):
        """Parse LaTeX content into slides"""
        self.slides = []

        # Extract preamble (everything before \begin{document})
        doc_start = content.find(r'\begin{document}')
        if doc_start == -1:
            raise ValueError("Invalid LaTeX file: missing \\begin{document}")

        self.preamble = content[:doc_start]
        remaining_content = content[doc_start + len(r'\begin{document}'):]

        # Extract title info from preamble
        self._extract_title_info_from_preamble()

        # Parse frames
        frame_pattern = re.compile(
            r'\\begin\{frame\}(.*?)\\end\{frame\}',
            re.DOTALL
        )

        for frame_match in frame_pattern.finditer(remaining_content):
            frame_content = frame_match.group(1)

            # Extract title
            title_match = re.search(r'\\frametitle\{(.*?)\}', frame_content)
            title = title_match.group(1) if title_match else "Untitled Slide"

            # Extract notes
            notes_match = re.search(r'\\note\{(.*?)\}', frame_content, re.DOTALL)
            notes = notes_match.group(1).split('\n') if notes_match else []

            # Extract media
            media_match = re.search(r'\\includegraphics.*?\{(.*?)\}', frame_content)
            media = media_match.group(1) if media_match else None

            # Clean content (remove notes and title)
            clean_content = re.sub(r'\\note\{.*?\}', '', frame_content, flags=re.DOTALL)
            clean_content = re.sub(r'\\frametitle\{.*?\}', '', clean_content)

            self.slides.append(Slide(
                title=title,
                content=[line.strip() for line in clean_content.split('\n') if line.strip()],
                notes=notes,
                media=media
            ))

        # Remove empty slides
        self.slides = [slide for slide in self.slides if slide.title or slide.content]

    def _extract_title_info_from_preamble(self):
        """Extract title info from LaTeX preamble"""
        title_match = re.search(r'\\title\{(.*?)\}', self.preamble)
        subtitle_match = re.search(r'\\subtitle\{(.*?)\}', self.preamble)
        author_match = re.search(r'\\author\{(.*?)\}', self.preamble)
        institute_match = re.search(r'\\institute\{(.*?)\}', self.preamble)
        date_match = re.search(r'\\date\{(.*?)\}', self.preamble)
        logo_match = re.search(r'\\includegraphics.*?\{(.*?)\}', self.preamble)

        self.title_info = {
            'title': title_match.group(1) if title_match else "Untitled Presentation",
            'subtitle': subtitle_match.group(1) if subtitle_match else "",
            'author': author_match.group(1) if author_match else "",
            'institute': institute_match.group(1) if institute_match else "",
            'date': date_match.group(1) if date_match else r"\today",
            'logo': logo_match.group(1) if logo_match else ""
        }


    def _generate_latex_from_slides(self):
        """Generate LaTeX with media and citation support"""
        latex = []

        # Preamble handling (keep existing)
        if r'\begin{document}' not in self.preamble:
            latex.append(self.preamble)

            if r'\title{' not in self.preamble:
                latex.append(r"\title{" + self.title_info['title'] + "}")
                if self.title_info['subtitle']:
                    latex.append(r"\subtitle{" + self.title_info['subtitle'] + "}")
                if self.title_info['author']:
                    latex.append(r"\author{" + self.title_info['author'] + "}")
                if self.title_info['institute']:
                    latex.append(r"\institute{" + self.title_info['institute'] + "}")
                if self.title_info['date']:
                    latex.append(r"\date{" + self.title_info['date'] + "}")

            latex.append(r"\begin{document}")

            if r'\titlepage' not in self.preamble:
                latex.append(r"\begin{frame}[plain]")
                latex.append(r"\titlepage")
                if self.title_info['logo']:
                    latex.append(r"\vspace{-2em}\centering\includegraphics[height=1cm]{" + self.title_info['logo'] + "}")
                latex.append(r"\end{frame}")
        else:
            latex.append(self.preamble)

        # Slide generation
        for slide in self.slides:
            latex.append(r"\begin{frame}")
            latex.append(r"\frametitle{" + slide.title + "}")

            # Handle media with citations
            if slide.media:
                # Get local path and citation
                media_path, citation = self.fetch_media(slide.media)

                if media_path:
                    latex.append(r"\begin{columns}")
                    latex.append(r"\column{0.5\textwidth}")

                    # Add content
                    in_list = False
                    for line in slide.content:
                        if line.startswith('- '):
                            if not in_list:
                                latex.append(r"\begin{itemize}")
                                in_list = True
                            latex.append(r"\item " + line[2:])
                        else:
                            if in_list:
                                latex.append(r"\end{itemize}")
                                in_list = False
                            latex.append(line)

                    if in_list:
                        latex.append(r"\end{itemize}")

                    # Add media column
                    latex.append(r"\column{0.5\textwidth}")
                    if media_path.endswith(('.mp4','.avi','.mov','.webm')):
                        latex.append(r"\movie[autostart]{\includegraphics[width=\textwidth]{placeholder}}{" + media_path + "}")
                    else:
                        latex.append(r"\includegraphics[width=\textwidth]{" + media_path + "}")

                    # Add citation if available
                    if citation:
                        # Ensure citation is properly escaped
                        escaped_citation = citation.replace('\\url{', '').replace('}', '')
                        latex.append(r"\vfill\footnotesize\textcolor{gray}{" + escaped_citation + "}")

                    latex.append(r"\end{columns}")

            # Handle slides without media
            else:
                in_list = False
                for line in slide.content:
                    if line.startswith('- '):
                        if not in_list:
                            latex.append(r"\begin{itemize}")
                            in_list = True
                        latex.append(r"\item " + line[2:])
                    else:
                        if in_list:
                            latex.append(r"\end{itemize}")
                            in_list = False
                        latex.append(line)

                if in_list:
                    latex.append(r"\end{itemize}")

            # Add notes if they exist
            if slide.notes:
                latex.append(r"\note{")
                latex.extend(slide.notes)
                latex.append(r"}")

            latex.append(r"\end{frame}")

        latex.append(self.postamble)
        return "\n".join(latex)

    def get_full_document(self):
        """Generate complete document content"""
        if self.is_text_file:
            return self._generate_latex_from_slides()
        else:
            return self.preamble + r"\begin{document}" + "\n".join(
                self._generate_slide_latex(slide) for slide in self.slides
            ) + self.postamble

    def _generate_slide_latex(self, slide):
        """Generate LaTeX for a single slide with proper media handling"""
        latex = []
        latex.append(r"\begin{frame}")

        # Process title with Unicode and special character handling
        processed_title = process_math_mode_segments(slide.title)
        latex.append(r"\frametitle{" + processed_title + "}")

        for line in slide.content:
            processed_line = process_math_mode_segments(line)
            latex.append(processed_line)

        # Similarly for notes
        if slide.notes:
            latex.append(r"\note{")
            for note in slide.notes:
                processed_note = process_math_mode_segments(note)
                latex.append(processed_note)
            latex.append(r"}")

        # Process content lines - convert Unicode FIRST, then escape
        in_math_mode = False
        for line in slide.content:
            # Convert Unicode to LaTeX first
            line = convert_unicode_to_latex(line)

            # Track math mode state
            math_mode_segments = re.split(r'(\$.*?\$|\\\(.*?\\\)|\\\[.*?\\\])', line)
            processed_line = []

            for segment in math_mode_segments:
                if segment.startswith('$') or segment.startswith(r'\(') or segment.startswith(r'\['):
                    # Inside math mode - don't escape special chars
                    processed_line.append(segment)
                else:
                    # Outside math mode - escape special chars
                    processed_line.append(escape_latex_special_chars(segment))

            line = ''.join(processed_line)
            latex.append(line)

        # Process content lines
        for line in slide.content:
            processed_line = escape_latex_special_chars(
                convert_unicode_to_latex(line)
            )

        latex.append(r"\frametitle{" + slide.title + "}")

        if slide.media:
            # Get local path and citation
            media_path, citation = self.fetch_media(slide.media)

            if media_path:
                latex.append(r"\begin{columns}")
                latex.append(r"\column{0.5\textwidth}")

                # Add content
                in_list = False
                for line in slide.content:
                    if line.startswith('- '):
                        if not in_list:
                            latex.append(r"\begin{itemize}")
                            in_list = True
                        latex.append(r"\item " + line[2:])
                    else:
                        if in_list:
                            latex.append(r"\end{itemize}")
                            in_list = False
                        latex.append(line)

                if in_list:
                    latex.append(r"\end{itemize}")

                # Add media column
                latex.append(r"\column{0.5\textwidth}")
                if media_path.endswith(('.mp4','.avi','.mov','.webm')):
                    latex.append(r"\movie[autostart]{\includegraphics[width=\textwidth]{placeholder}}{" + media_path + "}")
                else:
                    latex.append(r"\includegraphics[width=\textwidth]{" + media_path + "}")

                # Add citation if available
                if citation:
                    escaped_citation = citation.replace('\\url{', '').replace('}', '')
                    latex.append(r"\vfill\footnotesize\textcolor{gray}{" + escaped_citation + "}")


                latex.append(r"\end{columns}")
            else:
                # Media not found - add warning comment
                latex.append(r"% WARNING: Could not load media: " + slide.media)
                # Add content without media columns
                in_list = False
                for line in slide.content:
                    if line.startswith('- '):
                        if not in_list:
                            latex.append(r"\begin{itemize}")
                            in_list = True
                        latex.append(r"\item " + line[2:])
                    else:
                        if in_list:
                            latex.append(r"\end{itemize}")
                            in_list = False
                        latex.append(line)

                if in_list:
                    latex.append(r"\end{itemize}")

        else:
            # Handle slides without media
            in_list = False
            for line in slide.content:
                if line.startswith('- '):
                    if not in_list:
                        latex.append(r"\begin{itemize}")
                        in_list = True
                    latex.append(r"\item " + line[2:])
                else:
                    if in_list:
                        latex.append(r"\end{itemize}")
                        in_list = False
                    latex.append(line)

            if in_list:
                latex.append(r"\end{itemize}")

        # Add notes if they exist
        if slide.notes:
            latex.append(r"\note{")
            latex.extend(slide.notes)
            latex.append(r"}")

        latex.append(r"\end{frame}")
        return "\n".join(latex)

    def save_generated_tex(self):
        """Save the generated LaTeX to a file"""
        if not self.current_file:
            return ""

        tex_path = os.path.splitext(self.current_file)[0] + "_generated.tex"
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(self.get_full_document())
        return tex_path

# --------------------------
# Main Application
# --------------------------
class BeamerIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config.load()
        self.presentation = PresentationManager(write_terminal_callback=self.write_to_terminal)  # Pass callback
        self.current_file = None
        self.current_slide_index = 0

        self.setup_ui()
        self.setup_connections()
        self.setup_menu()
        self.apply_theme()

    def setup_ui(self):
        self.setWindowTitle("Beamer IDE - 4-Panel Editor")
        self.resize(1600, 900)

        # Main vertical splitter
        self.main_splitter = QSplitter(Qt.Vertical)

        # 1. Top section - Navigation controls
        self.setup_slide_navigation()

        # 2. Middle section - Main editor area
        middle_splitter = QSplitter(Qt.Horizontal)

        # Left panel - File browser
        self.file_browser = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.config.settings['working_directory'])
        self.file_browser.setModel(self.file_model)
        self.file_browser.setRootIndex(self.file_model.index(self.config.settings['working_directory']))
        self.file_browser.setColumnWidth(0, 250)
        self.file_browser.setMaximumWidth(300)

        # Center panel - 4-Panel editor
        self.editor_splitter = QSplitter(Qt.Vertical)
        self.setup_four_panel_editor()

        # Right panel - Preview and terminal
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        self.preview_label = QLabel("PDF Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: white;")
        right_layout.addWidget(self.preview_label, stretch=3)

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("background-color: black; color: white;")
        right_layout.addWidget(self.terminal_output, stretch=1)

        right_panel.setLayout(right_layout)

        # Add panels to middle splitter
        middle_splitter.addWidget(self.file_browser)
        middle_splitter.addWidget(self.editor_splitter)
        middle_splitter.addWidget(right_panel)
        middle_splitter.setSizes([200, 800, 400])

        # 3. Bottom section - Action buttons
        button_panel = QWidget()
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("padding: 5px; min-width: 80px;")
        button_layout.addWidget(self.save_btn)

        self.compile_btn = QPushButton("Compile PDF")
        self.compile_btn.setStyleSheet("padding: 5px; min-width: 80px;")
        button_layout.addWidget(self.compile_btn)

        button_panel.setLayout(button_layout)

        # Add all sections to main splitter
        self.main_splitter.addWidget(self.slide_nav_widget)
        self.main_splitter.addWidget(middle_splitter)
        self.main_splitter.addWidget(button_panel)
        self.main_splitter.setSizes([100, 700, 50])

        self.setCentralWidget(self.main_splitter)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Error dock
        self.setup_error_editor()

    def setup_error_editor(self):
        """Add a dockable editor for fixing LaTeX errors"""
        self.error_dock = QDockWidget("LaTeX Error Corrector", self)
        self.error_editor = QTextEdit()
        self.error_editor.setFont(QFont("Courier New", 10))
        self.error_dock.setWidget(self.error_editor)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.error_dock)
        self.error_dock.setVisible(False)


    def setup_four_panel_editor(self):
        """Initialize the 4-panel editor with enhanced media support"""
        # Panel 1: Title Editor
        self.title_editor = QTextEdit()
        self.title_editor.setPlaceholderText("Slide Title")
        self.title_editor.setFont(QFont("Courier New", self.config.settings['font_size']))

        # Panel 2: Graphics/Media (enhanced)
        self.graphics_panel = QWidget()
        graphics_layout = QVBoxLayout()

        self.graphics_path = QLineEdit()
        self.graphics_path.setPlaceholderText("Image/Video URL or Path")
        graphics_layout.addWidget(self.graphics_path)

        self.graphics_browse_btn = QPushButton("Add Media...")
        self.graphics_browse_btn.clicked.connect(self.browse_media)
        graphics_layout.addWidget(self.graphics_browse_btn)

        self.graphics_preview = QWidget()
        self.graphics_preview_layout = QVBoxLayout()
        self.graphics_preview.setLayout(self.graphics_preview_layout)
        graphics_layout.addWidget(self.graphics_preview, 1)

        self.graphics_panel.setLayout(graphics_layout)

        # Panel 3: Content Editor
        self.content_editor = QTextEdit()
        self.content_editor.setPlaceholderText("Slide Content")
        self.content_editor.setFont(QFont("Courier New", self.config.settings['font_size']))
        self.highlighter = BeamerSyntaxHighlighter(self.content_editor.document())

        # Panel 4: Notes Editor
        self.notes_editor = QTextEdit()
        self.notes_editor.setPlaceholderText("Speaker Notes")
        self.notes_editor.setFont(QFont("Courier New", self.config.settings['font_size']))

        # Add panels to splitter
        self.editor_splitter.addWidget(self.title_editor)
        self.editor_splitter.addWidget(self.graphics_panel)
        self.editor_splitter.addWidget(self.content_editor)
        self.editor_splitter.addWidget(self.notes_editor)

        # Set relative sizes
        self.editor_splitter.setSizes([100, 150, 400, 200])

    def setup_slide_navigation(self):
        """Setup slide navigation controls"""
        self.slide_nav_widget = QWidget()
        layout = QHBoxLayout()

        # Slide selector combo
        self.slide_selector = QComboBox()
        self.slide_selector.currentIndexChanged.connect(self.load_slide)
        layout.addWidget(QLabel("Current Slide:"))
        layout.addWidget(self.slide_selector, 1)

        # Navigation buttons
        self.prev_btn = QPushButton("◄ Previous")
        self.prev_btn.clicked.connect(self.prev_slide)
        layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next ►")
        self.next_btn.clicked.connect(self.next_slide)
        layout.addWidget(self.next_btn)

        # Slide operations
        self.add_slide_btn = QPushButton("+ Add Slide")
        self.add_slide_btn.clicked.connect(self.add_slide)
        layout.addWidget(self.add_slide_btn)

        self.del_slide_btn = QPushButton("× Delete Slide")
        self.del_slide_btn.clicked.connect(self.delete_slide)
        layout.addWidget(self.del_slide_btn)

        self.move_up_btn = QPushButton("↑ Move Up")
        self.move_up_btn.clicked.connect(self.move_slide_up)
        layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("↓ Move Down")
        self.move_down_btn.clicked.connect(self.move_slide_down)
        layout.addWidget(self.move_down_btn)

        self.slide_nav_widget.setLayout(layout)

    def setup_menu(self):
        """Setup the main menu"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        add_slide_action = QAction("Add Slide", self)
        add_slide_action.triggered.connect(self.add_slide)
        edit_menu.addAction(add_slide_action)

        edit_preamble_action = QAction("Edit Preamble", self)
        edit_preamble_action.triggered.connect(self.edit_preamble)
        edit_menu.addAction(edit_preamble_action)

        edit_title_action = QAction("Edit Title Info", self)
        edit_title_action.triggered.connect(self.edit_title_info)
        edit_menu.addAction(edit_title_action)

        # View menu
        view_menu = menubar.addMenu("View")

        self.dark_mode_action = QAction("Toggle Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.config.settings['theme'] == 'dark')
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)

        # Presentation menu
        pres_menu = menubar.addMenu("Presentation")

        compile_action = QAction("Compile PDF", self)
        compile_action.triggered.connect(self.compile_pdf)
        pres_menu.addAction(compile_action)

        present_action = QAction("Start Presentation", self)
        present_action.triggered.connect(self.start_presentation)
        pres_menu.addAction(present_action)


    def setup_connections(self):
        """Connect all UI signals to their slots"""
        # File browser
        self.file_browser.doubleClicked.connect(self.on_file_double_click)

        # Navigation controls
        self.slide_selector.currentIndexChanged.connect(self.load_slide)
        self.prev_btn.clicked.connect(self.prev_slide)
        self.next_btn.clicked.connect(self.next_slide)
        self.add_slide_btn.clicked.connect(self.add_slide)
        self.del_slide_btn.clicked.connect(self.delete_slide)
        self.move_up_btn.clicked.connect(self.move_slide_up)
        self.move_down_btn.clicked.connect(self.move_slide_down)

        # Editor connections
        self.title_editor.textChanged.connect(self.update_current_slide)
        self.content_editor.textChanged.connect(self.update_current_slide)
        self.notes_editor.textChanged.connect(self.update_current_slide)
        self.graphics_path.textChanged.connect(self.update_current_slide)
        self.graphics_browse_btn.clicked.connect(self.browse_media)  # Connected here

        # Action buttons
        self.save_btn.clicked.connect(self.save_file)
        self.compile_btn.clicked.connect(self.compile_pdf)


    def browse_media(self):
        """Handle media browsing for the current slide"""
        if not self.presentation.slides or self.current_slide_index < 0:
            QMessageBox.warning(self, "Warning", "Please create or select a slide first")
            return

        # Get current slide title for context
        slide_title = self.presentation.slides[self.current_slide_index].title

        # Create and show the media dialog
        dialog = MediaDownloadDialog(self, slide_title)
        if dialog.exec_() == QDialog.Accepted and dialog.url_input.text():
            media_url = dialog.url_input.text()

            # Use PresentationManager to handle the media
            local_path, citation = self.presentation.fetch_media(media_url)

            if local_path:
                # Update UI
                self.graphics_path.setText(media_url)
                self.update_media_preview(local_path)

                # Add citation to notes if it's a URL
                if citation and validators.url(media_url):
                    current_notes = self.notes_editor.toPlainText()
                    if citation not in current_notes:
                        self.notes_editor.setPlainText(
                            f"{current_notes}\nMedia Citation: {citation}".strip()
                        )

                # Update the current slide's media reference
                self.update_current_slide()

    def apply_theme(self):
        """Apply the current theme to the application"""
        if self.config.settings['theme'] == 'dark':
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            self.setPalette(dark_palette)
        else:
            self.setPalette(QPalette())

    def toggle_dark_mode(self):
        """Toggle between dark and light themes"""
        if self.dark_mode_action.isChecked():
            self.config.settings['theme'] = 'dark'
        else:
            self.config.settings['theme'] = 'light'

        self.config.save_config()
        self.apply_theme()

    def write_to_terminal(self, text, color="white"):
        """Write colored text to terminal output"""
        self.terminal_output.setTextColor(QColor(color))
        self.terminal_output.append(text)
        self.terminal_output.moveCursor(QTextCursor.End)

    def update_slide_selector(self):
        """Update the slide dropdown with current slide titles"""
        self.slide_selector.blockSignals(True)
        self.slide_selector.clear()

        for i, slide in enumerate(self.presentation.slides):
            title = slide.title if slide.title else f"Slide {i+1}"
            self.slide_selector.addItem(title)

        self.slide_selector.setCurrentIndex(self.current_slide_index)
        self.slide_selector.blockSignals(False)

    def clear_media_preview(self):
        """Properly clear the media preview area"""
        # Remove all widgets from the layout
        while self.graphics_preview_layout.count():
            child = self.graphics_preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add back the default label
        default_label = QLabel("Media Preview")
        default_label.setAlignment(Qt.AlignCenter)
        self.graphics_preview_layout.addWidget(default_label)

    def load_slide(self, index):
        """Load slide data into the 4-panel editor with proper media preview handling"""
        if not self.presentation.slides or index < 0 or index >= len(self.presentation.slides):
            # Clear all editors
            self.title_editor.clear()
            self.content_editor.clear()
            self.notes_editor.clear()
            self.graphics_path.clear()

            # Clear preview properly
            self.clear_media_preview()
            return

        self.current_slide_index = index

        # Block signals to prevent recursive updates
        self.title_editor.blockSignals(True)
        self.content_editor.blockSignals(True)
        self.notes_editor.blockSignals(True)
        self.graphics_path.blockSignals(True)

        # Load data into editors
        slide = self.presentation.slides[index]
        self.title_editor.setPlainText(slide.title)
        self.content_editor.setPlainText("\n".join(slide.content))
        self.notes_editor.setPlainText("\n".join(slide.notes))
        self.graphics_path.setText(slide.media or "")

        # Clear existing preview first
        self.clear_media_preview()

        # Update media preview if available
        if slide.media:
            if slide.media.startswith(('http://', 'https://')):
                # Show URL preview
                label = QLabel(f'<a href="{slide.media}">Media URL: {slide.media}</a>')
                label.setOpenExternalLinks(True)
                self.graphics_preview_layout.addWidget(label)
            else:
                # Show local file preview
                self.update_media_preview(slide.media)

        # Restore signals
        self.title_editor.blockSignals(False)
        self.content_editor.blockSignals(False)
        self.notes_editor.blockSignals(False)
        self.graphics_path.blockSignals(False)

        # Update navigation state
        self.update_nav_buttons()

    def update_current_slide(self):
        """Update the current slide with editor contents"""
        if not (0 <= self.current_slide_index < len(self.presentation.slides)):
            return

        slide = self.presentation.slides[self.current_slide_index]
        slide.title = self.title_editor.toPlainText()
        slide.content = self.content_editor.toPlainText().split('\n')
        slide.notes = self.notes_editor.toPlainText().split('\n')
        slide.media = self.graphics_path.text() if self.graphics_path.text() else None

        # Update slide selector if title changed
        self.slide_selector.setItemText(self.current_slide_index, slide.title)

    def update_nav_buttons(self):
        """Update the enabled/disabled state of navigation buttons"""
        self.prev_btn.setEnabled(self.current_slide_index > 0)
        self.next_btn.setEnabled(self.current_slide_index < len(self.presentation.slides) - 1)
        self.del_slide_btn.setEnabled(len(self.presentation.slides) > 1)
        self.move_up_btn.setEnabled(self.current_slide_index > 0)
        self.move_down_btn.setEnabled(self.current_slide_index < len(self.presentation.slides) - 1)



    def update_media_preview(self, media_path):
        """Update media preview with proper clearing"""
        self.clear_media_preview()

        if not media_path:
            return

        try:
            if media_path.lower().endswith(('.png','.jpg','.jpeg','.gif','.bmp')):
                pixmap = QPixmap(media_path)
                if not pixmap.isNull():
                    label = QLabel()
                    label.setPixmap(pixmap.scaled(
                        self.graphics_preview.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    ))
                    self.graphics_preview_layout.addWidget(label)

                    path_label = QLabel(f'<a href="{Path(media_path).absolute()}">{Path(media_path).name}</a>')
                    path_label.setOpenExternalLinks(True)
                    self.graphics_preview_layout.addWidget(path_label)

            elif media_path.lower().endswith(('.mp4','.avi','.mov','.webm')):
                label = QLabel(f"Video: {Path(media_path).name}")
                self.graphics_preview_layout.addWidget(label)

                path_label = QLabel(f'<a href="{Path(media_path).absolute()}">Open Video</a>')
                path_label.setOpenExternalLinks(True)
                self.graphics_preview_layout.addWidget(path_label)

        except Exception as e:
            error_label = QLabel(f"Error loading preview: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.graphics_preview_layout.addWidget(error_label)

    def new_file(self):
        """Create a new presentation"""
        if self.presentation.slides:
            reply = QMessageBox.question(
                self, 'New File',
                'Save current presentation before creating new file?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        self.presentation = PresentationManager()
        self.presentation.preamble = self.config.settings['default_preamble']
        self.add_slide()
        self.current_file = None
        self.status_label.setText("New Presentation")
        self.write_to_terminal("Created new presentation", "green")

    def open_file(self):
        """Open a presentation file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File",
            self.config.settings['working_directory'],
            "All Files (*);;Beamer Files (*.tex);;Text Files (*.txt)"
        )

        if file_path:
            try:
                self.presentation.load_file(file_path)
                self.current_file = file_path
                self.config.settings['working_directory'] = os.path.dirname(file_path)
                self.config.save_config()

                self.update_slide_selector()
                self.load_slide(0)
                self.write_to_terminal(f"Loaded: {os.path.basename(file_path)}", "green")
            except Exception as e:
                self.write_to_terminal(f"Error loading file: {str(e)}", "red")
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def save_file(self):
        """Save the current presentation"""
        if not self.current_file:
            self.save_file_as()
            return

        try:
            # Update current slide before saving
            self.update_current_slide()

            if self.presentation.is_text_file:
                # Save in simplified text format
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    # Save title info if present
                    if any(self.presentation.title_info.values()):
                        f.write(f"% Title: {self.presentation.title_info['title']}\n")
                        if self.presentation.title_info['subtitle']:
                            f.write(f"% Subtitle: {self.presentation.title_info['subtitle']}\n")
                        if self.presentation.title_info['author']:
                            f.write(f"% Author: {self.presentation.title_info['author']}\n")
                        if self.presentation.title_info['institute']:
                            f.write(f"% Institute: {self.presentation.title_info['institute']}\n")
                        if self.presentation.title_info['date']:
                            f.write(f"% Date: {self.presentation.title_info['date']}\n")
                        if self.presentation.title_info['logo']:
                            f.write(f"% Logo: {self.presentation.title_info['logo']}\n")
                        f.write("\n")

                    # Save slides
                    for slide in self.presentation.slides:
                        f.write(f"# {slide.title}\n")
                        if slide.media:
                            f.write(f"@media: {slide.media}\n")

                        # Save content
                        for line in slide.content:
                            f.write(f"{line}\n")

                        # Save notes if they exist
                        if slide.notes:
                            f.write("NOTES:\n")
                            for note in slide.notes:
                                f.write(f"{note}\n")

                        f.write("\n")

                self.write_to_terminal(f"Saved text version: {os.path.basename(self.current_file)}", "green")
            else:
                # Save as LaTeX
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.presentation.get_full_document())

                self.write_to_terminal(f"Saved LaTeX version: {os.path.basename(self.current_file)}", "green")

            self.status_label.setText(f"Saved: {os.path.basename(self.current_file)}")
        except Exception as e:
            self.write_to_terminal(f"Error saving file: {str(e)}", "red")
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def save_file_as(self):
        """Save the current presentation with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Presentation",
            self.config.settings['working_directory'],
            "Text Files (*.txt);;LaTeX Files (*.tex)"
        )

        if file_path:
            self.current_file = file_path
            self.config.settings['working_directory'] = os.path.dirname(file_path)
            self.config.save_config()
            self.save_file()

    def edit_preamble(self):
        """Edit the LaTeX preamble"""
        if self.presentation.is_text_file:
            QMessageBox.information(self, "Info", "Preamble editing is not available for text files")
            return

        preamble, ok = QInputDialog.getMultiLineText(
            self, "Edit Preamble",
            "Modify the LaTeX preamble:",
            self.presentation.preamble
        )

        if ok:
            self.presentation.preamble = preamble
            self.write_to_terminal("Preamble updated", "blue")

    def edit_title_info(self):
        """Edit the presentation title information"""
        title, ok1 = QInputDialog.getText(
            self, "Title Info", "Presentation Title:",
            text=self.presentation.title_info['title']
        )
        subtitle, ok2 = QInputDialog.getText(
            self, "Title Info", "Subtitle:",
            text=self.presentation.title_info['subtitle']
        )
        author, ok3 = QInputDialog.getText(
            self, "Title Info", "Author:",
            text=self.presentation.title_info['author']
        )
        institute, ok4 = QInputDialog.getText(
            self, "Title Info", "Institute:",
            text=self.presentation.title_info['institute'].replace(r"\textcolor{mygreen}{", "").replace("}", "")
        )
        date, ok5 = QInputDialog.getText(
            self, "Title Info", "Date:",
            text=self.presentation.title_info['date']
        )

        logo_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "", "Images (*.png *.jpg)"
        )

        if ok1 and ok2 and ok3 and ok4 and ok5:
            self.presentation.title_info = {
                'title': title,
                'subtitle': subtitle,
                'author': author,
                'institute': r"\textcolor{mygreen}{" + institute + "}",
                'date': date,
                'logo': logo_path
            }
            self.write_to_terminal("Title information updated", "blue")

    def add_slide(self):
        """Add a new slide to the presentation"""
        new_slide = Slide(
            title="New Slide",
            content=["- First item"],
            notes=["Speaker notes here"]
        )

        self.presentation.slides.append(new_slide)
        self.current_slide_index = len(self.presentation.slides) - 1
        self.update_slide_selector()
        self.load_slide(self.current_slide_index)

    def delete_slide(self):
        """Delete the current slide"""
        if len(self.presentation.slides) <= 1:
            QMessageBox.warning(self, "Warning", "You cannot delete the only remaining slide")
            return

        del self.presentation.slides[self.current_slide_index]

        if self.current_slide_index >= len(self.presentation.slides):
            self.current_slide_index = len(self.presentation.slides) - 1

        self.update_slide_selector()
        self.load_slide(self.current_slide_index)

    def prev_slide(self):
        """Navigate to the previous slide"""
        if self.current_slide_index > 0:
            self.current_slide_index -= 1
            self.load_slide(self.current_slide_index)

    def next_slide(self):
        """Navigate to the next slide"""
        if self.current_slide_index < len(self.presentation.slides) - 1:
            self.current_slide_index += 1
            self.load_slide(self.current_slide_index)

    def move_slide_up(self):
        """Move the current slide up in the sequence"""
        if self.current_slide_index > 0:
            self.presentation.slides.insert(
                self.current_slide_index - 1,
                self.presentation.slides.pop(self.current_slide_index)
            )
            self.current_slide_index -= 1
            self.update_slide_selector()

    def move_slide_down(self):
        """Move the current slide down in the sequence"""
        if self.current_slide_index < len(self.presentation.slides) - 1:
            self.presentation.slides.insert(
                self.current_slide_index + 1,
                self.presentation.slides.pop(self.current_slide_index)
            )
            self.current_slide_index += 1
            self.update_slide_selector()

    def on_file_double_click(self, index):
        """Handle double-click on file in browser"""
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            self.load_file(file_path)

    def navigate_to_error(self, error_line, explanation):
        """Enhanced error navigation with Unicode character highlighting"""
        if not error_line:
            return

        # Create a detailed tooltip
        tooltip = QLabel(explanation, self)
        tooltip.setWordWrap(True)
        tooltip.setStyleSheet("""
            QLabel {
                background-color: #ffffdc;
                padding: 10px;
                border: 2px solid #ff6b6b;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        tooltip.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)

        # Position near cursor
        cursor_pos = QCursor.pos()
        tooltip.move(cursor_pos.x() + 20, cursor_pos.y() + 20)
        tooltip.show()

        # Auto-close after 8 seconds
        QTimer.singleShot(8000, tooltip.deleteLater)

        # Find and highlight the problematic character
        tex_path = os.path.splitext(self.current_file)[0] + "_generated.tex"
        if os.path.exists(tex_path):
            with open(tex_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if error_line <= len(lines):
                error_text = lines[error_line - 1]
                unicode_match = re.search(r'[^\x00-\x7F]', error_text)

                if unicode_match:
                    # Navigate to slide containing the error
                    self.jump_to_error_slide(error_line, lines)

                    # Highlight the specific Unicode character
                    cursor = self.content_editor.textCursor()
                    cursor.movePosition(QTextCursor.Start)

                    # Find the line with the error
                    for _ in range(error_line - self.current_slide_start_line - 1):
                        cursor.movePosition(QTextCursor.Down)

                    # Find the Unicode character position
                    cursor.movePosition(QTextCursor.StartOfLine)
                    for _ in range(unicode_match.start()):
                        cursor.movePosition(QTextCursor.Right)

                    # Highlight the character
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
                    format = QTextCharFormat()
                    format.setBackground(QColor(255, 220, 220))
                    format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
                    format.setUnderlineColor(QColor(255, 0, 0))
                    cursor.mergeCharFormat(format)

                    # Show replacement suggestion
                    char = unicode_match.group()
                    if char in UNICODE_TO_LATEX:
                        suggestion = UNICODE_TO_LATEX[char]
                        self.status_label.setText(
                            f"Replace '{char}' with '{suggestion}'"
                        )
            # Position tooltip near editor
            editor_pos = self.content_editor.mapToGlobal(QPoint(0, 0))
            tooltip.move(editor_pos.x() + 50, editor_pos.y() + 50)
            tooltip.show()

            # Remove tooltip after 5 seconds
            QTimer.singleShot(5000, tooltip.deleteLater)

        # Read the generated tex file to map line numbers to slides
        tex_path = os.path.splitext(self.current_file)[0] + "_generated.tex"
        if not os.path.exists(tex_path):
            return

        with open(tex_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find which slide contains the error line
        current_line = 0
        slide_start_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith(r'\begin{frame}'):
                slide_start_lines.append(i)
            current_line += 1

            if current_line >= error_line:
                break

        if slide_start_lines:
            # The error is in the last frame we found before the error line
            error_slide_index = len(slide_start_lines) - 1
            if 0 <= error_slide_index < len(self.presentation.slides):
                self.current_slide_index = error_slide_index
                self.load_slide(error_slide_index)
                self.write_to_terminal(f"Navigated to slide {error_slide_index + 1} containing the error", "blue")

                # Highlight the problematic area in the editor
                self.content_editor.moveCursor(QTextCursor.Start)
                for _ in range(error_line - slide_start_lines[-1] - 1):
                    self.content_editor.moveCursor(QTextCursor.Down)

                # Create highlight effect
                cursor = self.content_editor.textCursor()
                format = QTextCharFormat()
                format.setBackground(QColor(255, 200, 200))  # Light red background
                cursor.select(QTextCursor.LineUnderCursor)
                cursor.mergeCharFormat(format)

                # Clear highlight after 3 seconds
                QTimer.singleShot(3000, lambda: self.clear_highlight())

    def clear_highlight(self):
        """Clear error highlight from editor"""
        cursor = self.content_editor.textCursor()
        format = QTextCharFormat()
        format.setBackground(QColor(255, 255, 255))  # White background
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.mergeCharFormat(format)

    def compile_pdf(self):
        """Compile the current presentation to PDF with error navigation"""
        if not self.presentation.slides:
            self.write_to_terminal("No slides to compile", "red")
            return False

        # Save before compiling
        self.save_file()

        working_dir = os.path.dirname(self.current_file) if self.current_file else os.getcwd()
        base_name = os.path.splitext(os.path.basename(self.current_file))[0] if self.current_file else "presentation"
        tex_file = base_name + ".tex"
        pdf_file = base_name + ".pdf"

        if self.presentation.is_text_file:
            tex_content = self.presentation.get_full_document()
            with open(os.path.join(working_dir, tex_file), 'w', encoding='utf-8') as f:
                f.write(tex_content)

        self.write_to_terminal(f"Compiling {tex_file}...", "blue")
        self.status_label.setText("Compiling...")
        QApplication.processEvents()

        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_file],
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                self.error_dock.show()
                error_line, explanation = self.parse_errors(result.stdout + result.stderr)
                if error_line:
                    self.navigate_to_error(error_line, explanation)

                # Navigate to problematic slide if error location found
                if error_line:
                    self.navigate_to_error(error_line)

                self.write_to_terminal("Compilation failed:", "red")
                self.status_label.setText("Compilation failed")
                return False

            # Second compilation for references
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file],
                cwd=working_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30
            )

            pdf_path = os.path.join(working_dir, pdf_file)
            if os.path.exists(pdf_path):
                self.error_dock.hide()
                self.write_to_terminal("Compilation successful!", "green")
                self.status_label.setText("Compilation successful")
                self.update_pdf_preview(pdf_path)
                return True
            else:
                self.error_dock.show()
                self.write_to_terminal("Error: PDF was not generated", "red")
                self.status_label.setText("PDF generation failed")
                return False

        except subprocess.TimeoutExpired:
            self.write_to_terminal("Error: Compilation timed out", "red")
            return False
        except Exception as e:
            self.write_to_terminal(f"Fatal error: {str(e)}", "red")
            return False

    def parse_errors(self, log_text):
        """Parse LaTeX errors and provide user-friendly explanations"""
        self.error_editor.clear()
        error_line = None
        error_explanation = ""
        # Add Unicode-specific error explanation
        UNICODE_ERROR_EXPLANATION = {
            "Unicode character": (
                "Unicode character detected that LaTeX can't process directly.\n\n"
                "Common solutions:\n"
                "1. Use the LaTeX equivalent (e.g., \\textsubscript{2} for ₂)\n"
                "2. Add \\usepackage[utf8]{inputenc} to preamble\n"
                "3. Use XeLaTeX or LuaLaTeX which have better Unicode support\n\n"
                "This editor can automatically convert these common Unicode characters:\n"
                "• Subscripts: ₂ → _{2}, ³ → ^3\n"
                "• Greek: α → \\alpha, β → \\beta\n"
                "• Math: ≤ → \\leq, ≈ → \\approx\n"
                "• Arrows: → → \\rightarrow\n"
            )
        }

        # Dictionary of common LaTeX errors and their explanations
        ERROR_EXPLANATIONS = {
            "Missing \\end{frame}": (
                "You're missing a closing \\end{frame} command.\n"
                "Solution: Add \\end{frame} after your slide content\n"
                "Tip: Check if you have matching \\begin{frame} and \\end{frame} pairs"
            ),
            "Undefined control sequence": (
                "You're using a LaTeX command that isn't defined.\n"
                "Common causes:\n"
                "1. Misspelled command (e.g., \\itemze instead of \\itemize)\n"
                "2. Missing package in preamble\n"
                "3. Using math symbols outside math mode ($...$)"
            ),
            "Missing $ inserted": (
                "You're using math symbols without proper math mode delimiters\n"
                "Solution: Enclose math expressions in $...$ or \\[...\\]\n"
                "Example: $E=mc^2$ instead of E=mc^2"
            ),
            "File not found": (
                "LaTeX can't find a file you referenced (image, bibliography, etc.)\n"
                "Check:\n"
                "1. File path is correct\n"
                "2. File exists in the specified location\n"
                "3. File extension is included"
            ),
            "Extra alignment tab": (
                "Problem with table/matrix alignment\n"
                "Common fixes:\n"
                "1. Check number of & separators in each row\n"
                "2. Ensure \\\\ at end of each row\n"
                "3. Verify environment (tabular, array, etc.) is properly closed"
            ),
            "Unicode character": (
                "You're using a Unicode character that LaTeX doesn't support directly.\n"
                "Solution: Use the LaTeX equivalent instead (e.g., \\textsubscript{2} for ₂)\n"
                "Tip: The editor can automatically convert many common Unicode characters"
            ),
            "Missing \\\\ inserted": (
                "Problem with special characters in tables/math mode\n"
                "Common fixes:\n"
                "1. Escape & with \\& outside tables\n"
                "2. Use $...$ for math expressions\n"
                "3. Double \\\\ for newlines in tables"
            )
        }
        # Update the error patterns to better catch Unicode errors
        error_patterns = [
            (r'! LaTeX Error: Unicode character (.*?) not set up',
             "Unicode character", UNICODE_ERROR_EXPLANATION["Unicode character"]),
            # ... keep other patterns ...
        ]

        for pattern, error_type, explanation in error_patterns:
            for match in re.finditer(pattern, log_text):
                error_line_match = re.search(r'l\.(\d+)', log_text[match.end():match.end()+100])
                if error_line_match:
                    error_line = int(error_line_match.group(1))
                    error_explanation = explanation

                    # Highlight the specific Unicode character if found
                    char_match = re.search(r'character (.*?) \(U\+', match.group(0))
                    if char_match:
                        error_explanation += f"\n\nDetected character: {char_match.group(1)}"

                        # Suggest replacement if available
                        unicode_char = char_match.group(1)
                        if unicode_char in UNICODE_TO_LATEX:
                            error_explanation += f"\nSuggested replacement: {UNICODE_TO_LATEX[unicode_char]}"

                    self.display_error(error_type, error_line, error_explanation, match.group(0))
        # Extract error messages with line numbers
        errors = re.finditer(
            r'(?P<error>! (?:LaTeX|Package) Error: (?P<errtype>.*?)\n(?P<errmsg>.*?\n.*?\n)',
            log_text,
            re.MULTILINE
        )

        for match in errors:
            error_type = match.group('errtype').strip()
            error_msg = match.group('errmsg').strip()
            line_match = re.search(r'l\.(\d+)', error_msg)
            line_num = int(line_match.group(1)) if line_match else None

            self.error_editor.setTextColor(QColor('red'))
            self.error_editor.append(f"ERROR: {error_type}")
            self.error_editor.append(f"Line: {line_num if line_num else 'unknown'}")
            self.error_editor.append("")

            # Add friendly explanation if available
            for known_error, explanation in ERROR_EXPLANATIONS.items():
                if known_error.lower() in error_type.lower():
                    self.error_editor.setTextColor(QColor('blue'))
                    self.error_editor.append("Explanation:")
                    self.error_editor.append(explanation)
                    self.error_editor.setTextColor(QColor('red'))
                    break

            self.error_editor.append("Raw error message:")
            self.error_editor.append(error_msg)
            self.error_editor.append("─" * 80)

            if line_num and not error_line:
                error_line = line_num
                error_explanation = next(
                    (exp for err, exp in ERROR_EXPLANATIONS.items()
                     if err.lower() in error_type.lower()),
                    ""
                )

        return error_line, error_explanation

    def display_error(self, error_type, line_num, explanation, raw_error):
        """Display formatted error in error editor"""
        self.error_editor.setTextColor(QColor('red'))
        self.error_editor.append(f"ERROR TYPE: {error_type}")
        self.error_editor.append(f"LINE: {line_num}")
        self.error_editor.append("")

        self.error_editor.setTextColor(QColor('blue'))
        self.error_editor.append("EXPLANATION:")
        self.error_editor.append(explanation)
        self.error_editor.append("")

        self.error_editor.setTextColor(QColor('darkRed'))
        self.error_editor.append("RAW ERROR MESSAGE:")
        self.error_editor.append(raw_error)
        self.error_editor.append("─" * 80)

    def update_pdf_preview(self, pdf_path):
        """Update the PDF preview panel"""
        if not os.path.exists(pdf_path):
            return

        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)  # Load first page
            zoom = 1.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # Convert to QImage
            img = QImage(
                pix.samples, pix.width, pix.height,
                pix.stride, QImage.Format_RGB888
            )

            # Scale to fit preview while maintaining aspect ratio
            scaled_img = img.scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.preview_label.setPixmap(QPixmap.fromImage(scaled_img))
            doc.close()
        except Exception as e:
            self.write_to_terminal(f"Error loading PDF preview: {str(e)}", "red")

    def start_presentation(self):
        """Start presentation with notes on second display"""
        if not self.current_file:
            self.write_to_terminal("Please save and compile first", "red")
            return

        pdf_file = os.path.splitext(self.current_file)[0] + ".pdf"

        if not os.path.exists(pdf_file):
            self.write_to_terminal("Please compile first", "red")
            return

        try:
            # Open presentation on primary display
            if sys.platform == "win32":
                os.startfile(pdf_file)
            elif sys.platform == "darwin":
                subprocess.run(["open", pdf_file])
            else:
                subprocess.run(["xdg-open", pdf_file])

            # Open notes on secondary display if available
            if hasattr(QDesktopWidget, 'screenCount') and QDesktopWidget().screenCount() > 1:
                notes_file = os.path.splitext(self.current_file)[0] + "_notes.pdf"
                if not os.path.exists(notes_file):
                    self.generate_notes_pdf()

                if sys.platform == "win32":
                    os.startfile(notes_file)
                elif sys.platform == "darwin":
                    subprocess.run(["open", "-n", notes_file])
                else:
                    subprocess.run(["xdg-open", notes_file])

        except Exception as e:
            self.write_to_terminal(f"Failed to start presentation: {str(e)}", "red")

    def generate_notes_pdf(self):
        """Generate a PDF with speaker notes"""
        if not self.current_file:
            return

        # Create a temporary LaTeX file with notes
        notes_tex = []
        notes_tex.append(self.presentation.preamble)
        notes_tex.append(r"\setbeameroption{show only notes}")
        notes_tex.append(r"\begin{document}")

        for slide in self.presentation.slides:
            notes_tex.append(r"\begin{frame}")
            notes_tex.append(r"\frametitle{" + slide.title + "}")

            if slide.notes:
                notes_tex.append(r"\note{")
                notes_tex.extend(slide.notes)
                notes_tex.append(r"}")

            notes_tex.append(r"\end{frame}")

        notes_tex.append(r"\end{document}")

        # Save and compile the notes file
        working_dir = os.path.dirname(self.current_file)
        base_name = os.path.splitext(os.path.basename(self.current_file))[0]
        notes_tex_file = os.path.join(working_dir, base_name + "_notes.tex")
        notes_pdf_file = os.path.join(working_dir, base_name + "_notes.pdf")

        with open(notes_tex_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(notes_tex))

        # Compile the notes PDF
        try:
            for _ in range(2):  # Run twice for proper references
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", notes_tex_file],
                    cwd=working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30
                )

            if os.path.exists(notes_pdf_file):
                self.write_to_terminal("Generated speaker notes PDF", "green")
            else:
                self.write_to_terminal("Failed to generate speaker notes", "red")
        except Exception as e:
            self.write_to_terminal(f"Error generating notes: {str(e)}", "red")


class BeamerSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Beamer LaTeX content"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_rules = []

        # Command highlighting
        command_format = QTextCharFormat()
        command_format.setForeground(QColor('#FF6B6B'))
        self.highlight_rules.append((r'\\[a-zA-Z]+', command_format))

        # Media highlighting
        media_format = QTextCharFormat()
        media_format.setForeground(QColor('#4ECDC4'))
        self.highlight_rules.append((r'\\includegraphics.*?\{(.*?)\}', media_format))

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        for pattern, format in self.highlight_rules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


def main():
    app = QApplication(sys.argv)

    # Create config directory if needed
    config = Config.load()
    if config.settings['theme'] == 'dark':
        app.setStyle("Fusion")
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.Text, Qt.white)
        app.setPalette(dark_palette)

    ide = BeamerIDE()

    # Open file from command line if specified
    if len(sys.argv) > 1:
        ide.load_file(sys.argv[1])
    elif config.settings['recent_files']:
        # Try to open most recent file
        try:
            ide.load_file(config.settings['recent_files'][0])
        except Exception:
            ide.new_file()
    else:
        ide.new_file()

    ide.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
