from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.markdown import Markdown
from rich.rule import Rule
from rich import box
from ..core.config import THEME, BANNER_ART

def render_banner():
    """
    Renders the ASCII banner with a gradient and subtitle.
    """
    # Create Text object from raw ASCII
    text = Text(BANNER_ART)
    
    # Apply Gradient
    # Characters 0-60: Bold White
    text.stylize("bold white", 0, 60)
    # Characters 60-200: Bold Accent
    text.stylize(f"bold {THEME['Accent']}", 60, 200)
    # Characters 200+: Bold Brand
    text.stylize(f"bold {THEME['Brand']}", 200)
    
    # Subtitle with background color
    subtitle = Text(" >> FINANCIAL INTELLIGENCE SYSTEM << ", style=f"bold #000000 on {THEME['Accent']}")
    
    # Panel with padding and breathing room
    panel = Panel(
        Align.center(text),
        padding=(2, 4),
        subtitle=subtitle,
        subtitle_align="center",
        border_style=THEME["Brand"],
        style=f"on {THEME['Background']}"
    )
    return panel

def render_mission_board(tasks):
    """
    Renders the list of tasks with status icons.
    """
    lines = []
    for task in tasks:
        status = task.get("status", "pending")
        description = task.get("description", "")
        detail = task.get("detail", "")
        
        icon = "○"
        style = THEME["Primary Text"]
        
        if status == "running":
            icon = "►"
            style = f"bold {THEME['Accent']}"
        elif status == "success":
            icon = "✔"
            style = f"bold {THEME['Success']}"
        elif status == "failed":
            icon = "✖"
            style = f"bold {THEME['Error']}"
        elif status == "pending":
            style = f"dim {THEME['Primary Text']}"

        lines.append(Text(f"{icon} {description}", style=style))
        
        # Show sub-step detail for running tasks
        if status == "running" and detail:
            lines.append(Text(f"  └─ {detail}", style=f"italic {THEME['Accent']}"))
            
    # Join lines with newlines
    content = Text("\n").join(lines) if lines else Text("No active tasks.")
    
    return Panel(
        content,
        title="[bold]MISSION CONTROL[/bold]",
        border_style=THEME["Brand"],
        padding=(1, 2),
        style=f"on {THEME['Background']}"
    )

def render_final_report(summary_text, data):
    """
    Renders a clean table for the final report.
    """
    # Summary (Markdown)
    summary = Markdown(summary_text)
    
    # Divider
    rule = Rule(style=THEME["Brand"])
    
    # Table
    table = Table(box=box.ROUNDED, show_header=True, header_style=f"bold {THEME['Accent']}", expand=True)
    table.add_column("Metric", style=f"bold {THEME['Accent']}")
    table.add_column("Value", justify="right", style="white")
    table.add_column("Source", style="dim white")
    
    for item in data:
        table.add_row(item["Metric"], item["Value"], item["Source"])
        
    # Footer
    footer = Text("Source: Jasper Financial Intelligence", style="dim white", justify="center")

    # Group
    group = Group(
        summary,
        Text("\n"),
        rule,
        Text("\n"),
        table,
        Text("\n"),
        footer
    )
    
    return Panel(
        group,
        title="[bold]FINAL INTELLIGENCE REPORT[/bold]",
        border_style=THEME["Brand"],
        style=f"on {THEME['Background']}",
        padding=(1, 2)
    )
