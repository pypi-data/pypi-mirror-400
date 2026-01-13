"""
Command Line Interface for Blog2Podcasts
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from blog2podcasts import __version__
from blog2podcasts.scraper import BlogScraper, BlogContent
from blog2podcasts.summarizer import ContentSummarizer
from blog2podcasts.audio_generator import AudioGenerator, RECOMMENDED_VOICES
from blog2podcasts.voice_cloner import VoiceCloner, ClonedVoiceGenerator, VoiceProfile

console = Console()


@dataclass
class PodcastConfig:
    """Configuration for podcast generation"""
    voice: str = "en-US-GuyNeural"
    model: str = "llama3.2"
    script_length: int = 800
    output_dir: str = "output"
    save_script: bool = True
    speech_rate: str = "+0%"
    speech_pitch: str = "+0Hz"
    cloned_voice: Optional[str] = None
    use_cloned_voice: bool = False


class BlogToPodcastAgent:
    """
    Agent that orchestrates the full blog-to-podcast pipeline:
    1. Scrape blog content from URL
    2. Generate podcast script using LLM
    3. Convert script to audio
    """
    
    def __init__(self, config: PodcastConfig = None):
        self.config = config or PodcastConfig()
        
        self.scraper = BlogScraper()
        self.summarizer = ContentSummarizer(model=self.config.model)
        
        self.voice_cloner = VoiceCloner()
        self.cloned_voice_generator = None
        self.voice_profile = None
        
        if self.config.use_cloned_voice and self.config.cloned_voice:
            self.voice_profile = self.voice_cloner.get_profile(self.config.cloned_voice)
            if self.voice_profile:
                self.cloned_voice_generator = ClonedVoiceGenerator()
                console.print(f"[green]✓ Using cloned voice: {self.config.cloned_voice}[/green]")
            else:
                console.print(f"[yellow]⚠ Voice profile '{self.config.cloned_voice}' not found, using default voice[/yellow]")
        
        self.audio_generator = AudioGenerator(
            voice=self.config.voice,
            rate=self.config.speech_rate,
            pitch=self.config.speech_pitch
        )
        
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
    
    def convert(self, url: str, output_name: Optional[str] = None) -> dict:
        """Convert a blog URL to podcast audio"""
        console.print(Panel(
            f"[bold blue]🎙️ Blog to Podcast Agent[/bold blue]\n"
            f"Converting: {url}",
            title="Blog2Podcasts"
        ))
        
        # Step 1: Scrape content
        console.print("\n[bold]Step 1/3: Extracting content...[/bold]")
        content = self.scraper.scrape(url)
        
        # Step 2: Generate script
        console.print("\n[bold]Step 2/3: Generating podcast script...[/bold]")
        script = self.summarizer.generate_podcast_script(
            content=content.text,
            title=content.title,
            target_length=self.config.script_length
        )
        
        # Generate output filename
        if output_name:
            safe_name = re.sub(r'[^\w\s-]', '', output_name.lower())
        else:
            safe_name = re.sub(r'[^\w\s-]', '', content.title.lower())
        safe_name = re.sub(r'[-\s]+', '_', safe_name).strip('_')[:50]
        
        output_base = Path(self.config.output_dir) / safe_name
        
        # Save script if requested
        script_path = None
        if self.config.save_script:
            script_path = f"{output_base}_podcast.txt"
            with open(script_path, 'w') as f:
                f.write(f"# Podcast Script: {content.title}\n")
                f.write(f"# Source: {url}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                f.write(script)
            console.print(f"[green]✓ Script saved: {script_path}[/green]")
        
        # Step 3: Generate audio
        console.print("\n[bold]Step 3/3: Generating audio...[/bold]")
        
        import asyncio
        
        if self.cloned_voice_generator and self.voice_profile:
            audio_path = f"{output_base}_podcast.wav"
            audio_path = asyncio.run(
                self.cloned_voice_generator.generate_audio(
                    text=script,
                    output_path=audio_path,
                    voice_profile=self.voice_profile
                )
            )
        else:
            audio_path = f"{output_base}_podcast.mp3"
            audio_path = asyncio.run(
                self.audio_generator.generate_audio(script, audio_path)
            )
        
        # Summary
        console.print(Panel(
            f"[bold green]✓ Podcast generated successfully![/bold green]\n\n"
            f"📄 Title: {content.title}\n"
            f"🎵 Audio: {audio_path}\n"
            f"📝 Script: {script_path or 'Not saved'}",
            title="Complete"
        ))
        
        return {
            "title": content.title,
            "audio_path": audio_path,
            "script_path": script_path,
            "script": script
        }


def list_voices():
    """List all available Edge TTS voices"""
    import asyncio
    from blog2podcasts.audio_generator import AudioGenerator
    
    generator = AudioGenerator()
    voices = asyncio.run(generator.list_voices())
    
    console.print("\n[bold]Recommended Podcast Voices:[/bold]")
    for name, voice_id in RECOMMENDED_VOICES.items():
        console.print(f"  {name}: {voice_id}")
    
    console.print(f"\n[bold]All Available Voices ({len(voices)}):[/bold]")
    
    # Group by language
    by_locale = {}
    for v in voices:
        locale = v.locale[:5]
        if locale not in by_locale:
            by_locale[locale] = []
        by_locale[locale].append(v)
    
    for locale in sorted(by_locale.keys()):
        console.print(f"\n  [cyan]{locale}:[/cyan]")
        for v in by_locale[locale]:
            console.print(f"    {v.short_name} ({v.gender})")


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="🎙️ Blog2Podcasts - Convert blog articles to podcast audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  blog2podcasts https://example.com/blog-article
  blog2podcasts https://example.com/blog --voice en-GB-RyanNeural
  blog2podcasts https://example.com/blog --model mistral --length 1200
  blog2podcasts --list-voices
  blog2podcasts --clone-voice "https://youtube.com/watch?v=..." --voice-name "my_host"
        """
    )
    
    parser.add_argument("url", nargs="?", help="Blog URL to convert")
    parser.add_argument("-o", "--output", help="Custom output name")
    parser.add_argument("--voice", default="en-US-GuyNeural", help="TTS voice to use")
    parser.add_argument("--model", default="llama3.2", help="Ollama model for summarization")
    parser.add_argument("--length", type=int, default=800, help="Target script length (words)")
    parser.add_argument("--rate", default="+0%", help="Speech rate adjustment")
    parser.add_argument("--pitch", default="+0Hz", help="Pitch adjustment")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--preview", action="store_true", help="Preview script without audio")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    parser.add_argument("--clone-voice", help="YouTube URL to clone voice from")
    parser.add_argument("--voice-name", help="Name for cloned voice profile")
    parser.add_argument("--use-cloned-voice", help="Use a cloned voice profile")
    parser.add_argument("--version", action="version", version=f"blog2podcasts {__version__}")
    
    args = parser.parse_args()
    
    # List voices
    if args.list_voices:
        list_voices()
        return
    
    # Clone voice from YouTube
    if args.clone_voice:
        if not args.voice_name:
            console.print("[red]Error: --voice-name is required when cloning voice[/red]")
            return
        
        cloner = VoiceCloner()
        profile = cloner.extract_voice_from_youtube(args.clone_voice, args.voice_name)
        console.print(f"[green]✓ Voice profile '{profile.name}' created successfully![/green]")
        return
    
    # Convert blog to podcast
    if not args.url:
        parser.print_help()
        return
    
    config = PodcastConfig(
        voice=args.voice,
        model=args.model,
        script_length=args.length,
        output_dir=args.output_dir,
        save_script=True,
        speech_rate=args.rate,
        speech_pitch=args.pitch,
        cloned_voice=args.use_cloned_voice,
        use_cloned_voice=bool(args.use_cloned_voice)
    )
    
    agent = BlogToPodcastAgent(config)
    
    if args.preview:
        content = agent.scraper.scrape(args.url)
        script = agent.summarizer.generate_podcast_script(
            content=content.text,
            title=content.title,
            target_length=config.script_length
        )
        console.print(Panel(Markdown(script), title="Preview Script"))
    else:
        agent.convert(args.url, args.output)


if __name__ == "__main__":
    main()
