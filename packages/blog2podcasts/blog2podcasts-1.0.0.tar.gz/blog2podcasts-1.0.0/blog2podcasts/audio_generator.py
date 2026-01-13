"""
Audio Generator Module
Converts text to speech using Edge TTS (Microsoft's free TTS)
"""

import asyncio
import edge_tts
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


@dataclass
class VoiceOption:
    """Available voice configuration"""
    name: str
    short_name: str
    gender: str
    locale: str


# Popular voices for podcasts
RECOMMENDED_VOICES = {
    "male_us": "en-US-GuyNeural",
    "female_us": "en-US-JennyNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_au": "en-AU-WilliamNeural",
    "female_au": "en-AU-NatashaNeural",
}


class AudioGenerator:
    """Generates podcast audio from text using Edge TTS"""
    
    def __init__(self, voice: str = "en-US-GuyNeural", rate: str = "+0%", pitch: str = "+0Hz"):
        """
        Initialize audio generator
        
        Args:
            voice: Voice name (use list_voices() to see options)
            rate: Speech rate adjustment (e.g., "+10%", "-5%")
            pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
        """
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
    
    async def generate_audio(self, text: str, output_path: str) -> str:
        """
        Generate audio file from text
        
        Args:
            text: Text to convert to speech
            output_path: Path for output audio file
            
        Returns:
            Path to generated audio file
        """
        console.print(f"[blue]🎵 Generating audio with voice: {self.voice}[/blue]")
        
        # Clean text for better TTS
        text = self._prepare_text(text)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(description="Converting text to speech...", total=100)
                
                # Create communicate object
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=self.voice,
                    rate=self.rate,
                    pitch=self.pitch
                )
                
                progress.update(task, advance=30)
                
                # Ensure output directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Generate and save audio
                await communicate.save(output_path)
                
                progress.update(task, advance=70)
            
            console.print(f"[green]✓ Audio saved to: {output_path}[/green]")
            return output_path
            
        except Exception as e:
            console.print(f"[red]✗ Audio generation failed: {e}[/red]")
            raise
    
    def generate_audio_sync(self, text: str, output_path: str) -> str:
        """Synchronous wrapper for generate_audio"""
        return asyncio.run(self.generate_audio(text, output_path))
    
    def _prepare_text(self, text: str) -> str:
        """Prepare text for TTS processing"""
        # Handle pause markers
        text = text.replace("[PAUSE]", "...")
        text = text.replace("[pause]", "...")
        
        # Clean up extra whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = ' '.join(lines)
        
        # Add slight pauses after sentences for more natural speech
        text = text.replace(". ", ". ... ")
        text = text.replace("? ", "? ... ")
        text = text.replace("! ", "! ... ")
        
        return text
    
    @staticmethod
    async def list_voices(locale_filter: str = "en") -> List[VoiceOption]:
        """
        List available voices
        
        Args:
            locale_filter: Filter voices by locale (e.g., "en" for English)
            
        Returns:
            List of available voices
        """
        voices = await edge_tts.list_voices()
        
        filtered = []
        for voice in voices:
            if locale_filter.lower() in voice["Locale"].lower():
                filtered.append(VoiceOption(
                    name=voice["FriendlyName"],
                    short_name=voice["ShortName"],
                    gender=voice["Gender"],
                    locale=voice["Locale"]
                ))
        
        return filtered
    
    @staticmethod
    def list_voices_sync(locale_filter: str = "en") -> List[VoiceOption]:
        """Synchronous wrapper for list_voices"""
        return asyncio.run(AudioGenerator.list_voices(locale_filter))


def generate_podcast_audio(text: str, output_path: str, voice: str = "en-US-GuyNeural") -> str:
    """Convenience function to generate podcast audio"""
    generator = AudioGenerator(voice=voice)
    return generator.generate_audio_sync(text, output_path)


def print_available_voices():
    """Print available English voices"""
    console.print("\n[bold]Available English Voices:[/bold]\n")
    
    console.print("[bold]Recommended for Podcasts:[/bold]")
    for key, voice in RECOMMENDED_VOICES.items():
        console.print(f"  {key}: {voice}")
    
    console.print("\n[bold]All English Voices:[/bold]")
    voices = AudioGenerator.list_voices_sync("en")
    
    for voice in voices:
        console.print(f"  [{voice.gender}] {voice.short_name} - {voice.name}")


if __name__ == "__main__":
    # Test the audio generator
    print_available_voices()
    
    test_text = """
    Welcome to our podcast! Today we're exploring the fascinating world of 
    artificial intelligence. [PAUSE] 
    
    Let's dive into how AI is changing our daily lives.
    From smart assistants to self-driving cars, the future is here.
    
    Thanks for listening!
    """
    
    output = generate_podcast_audio(test_text, "output/test_podcast.mp3")
    print(f"\nGenerated: {output}")
