"""
Voice Cloner Module
Extracts voice signatures from YouTube videos for TTS cloning
Uses yt-dlp for downloading and Coqui TTS (XTTS-v2) for voice cloning
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import json

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


@dataclass
class VoiceProfile:
    """Extracted voice profile from YouTube"""
    name: str
    source_url: str
    audio_path: str
    channel_name: Optional[str] = None
    duration_seconds: float = 0


class VoiceCloner:
    """
    Extracts and clones voices from YouTube videos
    Uses XTTS-v2 for high-quality voice cloning
    """
    
    VOICES_DIR = "voices"
    MIN_AUDIO_DURATION = 10  # Minimum seconds for good voice cloning
    MAX_AUDIO_DURATION = 30  # Optimal duration for voice sample
    
    def __init__(self, voices_dir: str = None):
        """
        Initialize voice cloner
        
        Args:
            voices_dir: Directory to store voice profiles
        """
        self.voices_dir = Path(voices_dir or self.VOICES_DIR)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        
        self._tts_model = None
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required tools are installed"""
        import shutil
        import sys
        
        # Check yt-dlp (try Python module first, then system command)
        try:
            import yt_dlp
        except ImportError:
            if not shutil.which("yt-dlp"):
                console.print("[yellow]⚠ yt-dlp not found. Install with: pip install yt-dlp[/yellow]")
        
        # Check ffmpeg
        if not shutil.which("ffmpeg"):
            console.print("[yellow]⚠ ffmpeg not found. Install ffmpeg for audio processing[/yellow]")
    
    def extract_voice_from_youtube(
        self,
        url: str,
        profile_name: str,
        start_time: Optional[str] = None,
        duration: int = 30
    ) -> VoiceProfile:
        """
        Extract voice sample from a YouTube video
        
        Args:
            url: YouTube video or channel URL
            profile_name: Name for the voice profile
            start_time: Start time for extraction (e.g., "00:01:30")
            duration: Duration in seconds to extract
            
        Returns:
            VoiceProfile with extracted audio
        """
        console.print(f"[blue]🎤 Extracting voice from YouTube...[/blue]")
        
        # Sanitize profile name
        safe_name = re.sub(r'[^\w\s-]', '', profile_name.lower())
        safe_name = re.sub(r'[-\s]+', '_', safe_name).strip('_')
        
        profile_dir = self.voices_dir / safe_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        audio_path = profile_dir / "voice_sample.wav"
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                # Step 1: Get video info
                progress.add_task(description="Fetching video info...", total=None)
                video_info = self._get_video_info(url)
                
                # Step 2: Download audio
                progress.add_task(description="Downloading audio...", total=None)
                temp_audio = self._download_audio(url, start_time, duration)
                
                # Step 3: Process audio for voice cloning
                progress.add_task(description="Processing voice sample...", total=None)
                self._process_audio_for_cloning(temp_audio, str(audio_path))
                
                # Clean up temp file
                if os.path.exists(temp_audio):
                    os.remove(temp_audio)
            
            # Save profile metadata
            profile = VoiceProfile(
                name=safe_name,
                source_url=url,
                audio_path=str(audio_path),
                channel_name=video_info.get("channel", "Unknown"),
                duration_seconds=duration
            )
            
            self._save_profile_metadata(profile)
            
            console.print(f"[green]✓ Voice profile '{safe_name}' created successfully[/green]")
            console.print(f"  Audio saved: {audio_path}")
            
            return profile
            
        except Exception as e:
            console.print(f"[red]✗ Voice extraction failed: {e}[/red]")
            raise
    
    def _get_video_info(self, url: str) -> dict:
        """Get video metadata using yt-dlp Python API"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info if info else {}
        except Exception:
            return {}
    
    def _download_audio(self, url: str, start_time: Optional[str], duration: int) -> str:
        """Download audio from YouTube video using yt-dlp Python API"""
        import yt_dlp
        
        temp_file = tempfile.mktemp(suffix=".wav")
        output_template = temp_file.replace(".wav", ".%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
        # Add time range if specified
        if start_time:
            ydl_opts['download_ranges'] = yt_dlp.utils.download_range_func(
                None, [(self._parse_time(start_time), self._parse_time(start_time) + duration)]
            )
        else:
            ydl_opts['download_ranges'] = yt_dlp.utils.download_range_func(
                None, [(0, duration)]
            )
        ydl_opts['force_keyframes_at_cuts'] = True
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Find the downloaded file
        base = temp_file.replace(".wav", "")
        for ext in [".wav", ".webm", ".m4a", ".mp3", ".opus"]:
            if os.path.exists(base + ext):
                return base + ext
        
        # Check if file exists with original extension
        import glob
        files = glob.glob(base + ".*")
        if files:
            return files[0]
        
        return temp_file
    
    def _parse_time(self, time_str: str) -> float:
        """Parse time string (HH:MM:SS or MM:SS) to seconds"""
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        else:
            return float(time_str)
    
    def _process_audio_for_cloning(self, input_path: str, output_path: str):
        """
        Process audio to optimal format for voice cloning
        - Convert to mono 22050Hz WAV
        - Normalize audio levels
        - Remove silence
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", "22050",  # Sample rate for TTS
            "-ac", "1",      # Mono
            "-af", "silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,loudnorm",
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    def _save_profile_metadata(self, profile: VoiceProfile):
        """Save voice profile metadata"""
        metadata_path = self.voices_dir / profile.name / "metadata.json"
        
        with open(metadata_path, 'w') as f:
            json.dump({
                "name": profile.name,
                "source_url": profile.source_url,
                "audio_path": profile.audio_path,
                "channel_name": profile.channel_name,
                "duration_seconds": profile.duration_seconds
            }, f, indent=2)
    
    def list_profiles(self) -> List[VoiceProfile]:
        """List all saved voice profiles"""
        profiles = []
        
        for profile_dir in self.voices_dir.iterdir():
            if profile_dir.is_dir():
                metadata_path = profile_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path) as f:
                        data = json.load(f)
                        profiles.append(VoiceProfile(**data))
        
        return profiles
    
    def get_profile(self, name: str) -> Optional[VoiceProfile]:
        """Get a voice profile by name"""
        profile_dir = self.voices_dir / name
        metadata_path = profile_dir / "metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path) as f:
                data = json.load(f)
                return VoiceProfile(**data)
        
        return None
    
    def delete_profile(self, name: str) -> bool:
        """Delete a voice profile"""
        import shutil
        profile_dir = self.voices_dir / name
        
        if profile_dir.exists():
            shutil.rmtree(profile_dir)
            console.print(f"[green]✓ Profile '{name}' deleted[/green]")
            return True
        
        console.print(f"[yellow]Profile '{name}' not found[/yellow]")
        return False


class ClonedVoiceGenerator:
    """
    Generates audio using cloned voices via Coqui TTS (XTTS-v2)
    """
    
    def __init__(self):
        self._model = None
        self._model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    
    def _load_model(self):
        """Lazy load the TTS model"""
        if self._model is None:
            console.print("[blue]🔄 Loading XTTS-v2 model (first time may take a while)...[/blue]")
            
            try:
                from TTS.api import TTS
                self._model = TTS(self._model_name)
                console.print("[green]✓ Model loaded successfully[/green]")
            except ImportError:
                console.print("[red]✗ Coqui TTS not installed. Install with:[/red]")
                console.print("  pip install TTS")
                raise
            except Exception as e:
                console.print(f"[red]✗ Failed to load model: {e}[/red]")
                raise
        
        return self._model
    
    def generate_audio(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: str,
        language: str = "en"
    ) -> str:
        """
        Generate audio using a cloned voice
        
        Args:
            text: Text to convert to speech
            voice_profile: Voice profile to clone
            output_path: Path for output audio file
            language: Language code (default: en)
            
        Returns:
            Path to generated audio
        """
        console.print(f"[blue]🎵 Generating audio with cloned voice: {voice_profile.name}[/blue]")
        
        model = self._load_model()
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console,
            ) as progress:
                progress.add_task(description="Synthesizing speech...", total=None)
                
                # Generate with voice cloning
                model.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=voice_profile.audio_path,
                    language=language
                )
            
            console.print(f"[green]✓ Audio saved to: {output_path}[/green]")
            return output_path
            
        except Exception as e:
            console.print(f"[red]✗ Audio generation failed: {e}[/red]")
            raise
    
    def generate_audio_sync(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: str,
        language: str = "en"
    ) -> str:
        """Synchronous wrapper for generate_audio"""
        return self.generate_audio(text, voice_profile, output_path, language)


def extract_youtube_voice(url: str, profile_name: str, start_time: str = None) -> VoiceProfile:
    """Convenience function to extract voice from YouTube"""
    cloner = VoiceCloner()
    return cloner.extract_voice_from_youtube(url, profile_name, start_time)


def list_voice_profiles() -> List[VoiceProfile]:
    """Convenience function to list voice profiles"""
    cloner = VoiceCloner()
    return cloner.list_profiles()


def print_voice_profiles():
    """Print all saved voice profiles"""
    profiles = list_voice_profiles()
    
    if not profiles:
        console.print("[yellow]No voice profiles found. Create one with:[/yellow]")
        console.print("  python agent.py --clone-voice <youtube_url> --voice-name <name>")
        return
    
    console.print("\n[bold]Saved Voice Profiles:[/bold]\n")
    for profile in profiles:
        console.print(f"  [cyan]{profile.name}[/cyan]")
        console.print(f"    Channel: {profile.channel_name}")
        console.print(f"    Source: {profile.source_url}")
        console.print(f"    Duration: {profile.duration_seconds}s")
        console.print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Cloning from YouTube")
    parser.add_argument("--extract", "-e", help="YouTube URL to extract voice from")
    parser.add_argument("--name", "-n", help="Name for the voice profile")
    parser.add_argument("--start", "-s", help="Start time (e.g., '00:01:30')")
    parser.add_argument("--list", "-l", action="store_true", help="List saved profiles")
    parser.add_argument("--delete", "-d", help="Delete a voice profile")
    
    args = parser.parse_args()
    
    if args.list:
        print_voice_profiles()
    elif args.delete:
        cloner = VoiceCloner()
        cloner.delete_profile(args.delete)
    elif args.extract and args.name:
        profile = extract_youtube_voice(args.extract, args.name, args.start)
        print(f"\nCreated profile: {profile.name}")
    else:
        parser.print_help()
