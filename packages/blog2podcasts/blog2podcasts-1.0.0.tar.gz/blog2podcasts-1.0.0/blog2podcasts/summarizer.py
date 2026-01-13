"""
Content Summarizer Module
Uses Ollama for local LLM-based summarization
"""

import ollama
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class ContentSummarizer:
    """Summarizes blog content using local LLMs via Ollama"""
    
    DEFAULT_MODEL = "llama3.2"  # Default model, can be changed
    
    PODCAST_PROMPT = """You are a podcast script writer. Convert the following blog article into an engaging podcast script.

Guidelines:
- Write in a conversational, engaging tone suitable for audio
- Start with a compelling hook to grab listeners' attention
- Break down complex topics into digestible explanations
- Use transitions like "Now, let's talk about...", "Here's the interesting part...", "What's fascinating is..."
- Include brief pauses marked as [PAUSE] for natural speech rhythm
- End with a summary and call-to-action for listeners
- Keep the script around {target_length} words
- Do NOT include any stage directions, speaker labels, or sound effects beyond [PAUSE]
- Write as if a single host is speaking directly to the audience

Blog Title: {title}

Blog Content:
{content}

Generate the podcast script:"""

    SUMMARY_PROMPT = """Summarize the following blog article in a clear, concise manner.
Keep the main points and key insights. Target length: {target_length} words.

Blog Title: {title}

Blog Content:
{content}

Summary:"""

    def __init__(self, model: str = None):
        """
        Initialize the summarizer
        
        Args:
            model: Ollama model to use (default: llama3.2)
        """
        self.model = model or self.DEFAULT_MODEL
        self._verify_ollama()
    
    def _verify_ollama(self) -> bool:
        """Verify Ollama is running and model is available"""
        try:
            models_response = ollama.list()
            
            # Handle different response formats from ollama library
            if hasattr(models_response, 'models'):
                # Newer ollama library returns object with .models attribute
                models_list = models_response.models
                available_models = [m.model.split(':')[0] if hasattr(m, 'model') else str(m).split(':')[0] for m in models_list]
            elif isinstance(models_response, dict) and 'models' in models_response:
                # Older format returns dict
                models_list = models_response['models']
                available_models = [m.get('name', '').split(':')[0] for m in models_list]
            else:
                available_models = []
            
            if not available_models:
                console.print("[yellow]⚠ No models found. You may need to pull a model:[/yellow]")
                console.print(f"  Run: ollama pull {self.model}")
                return False
                
            # Check if requested model is available
            model_base = self.model.split(':')[0]
            if model_base not in available_models:
                console.print(f"[yellow]⚠ Model '{self.model}' not found. Available models:[/yellow]")
                for m in available_models:
                    console.print(f"  - {m}")
                console.print(f"\n[yellow]Run: ollama pull {self.model}[/yellow]")
                return False
                
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Ollama not available: {e}[/red]")
            console.print("[yellow]Make sure Ollama is installed and running:[/yellow]")
            console.print("  1. Install: https://ollama.ai")
            console.print("  2. Start: ollama serve")
            console.print(f"  3. Pull model: ollama pull {self.model}")
            return False
    
    def summarize(self, content: str, title: str = "", target_length: int = 300) -> str:
        """
        Create a summary of the content
        
        Args:
            content: The blog content to summarize
            title: The blog title
            target_length: Target word count for summary
            
        Returns:
            Summarized text
        """
        console.print(f"[blue]📝 Generating summary using {self.model}...[/blue]")
        
        prompt = self.SUMMARY_PROMPT.format(
            title=title,
            content=content[:8000],  # Limit content length for context window
            target_length=target_length
        )
        
        return self._generate(prompt)
    
    def create_podcast_script(self, content: str, title: str = "", target_length: int = 800) -> str:
        """
        Convert blog content into a podcast script
        
        Args:
            content: The blog content to convert
            title: The blog title
            target_length: Target word count for podcast script
            
        Returns:
            Podcast script ready for TTS
        """
        console.print(f"[blue]🎙️ Creating podcast script using {self.model}...[/blue]")
        
        prompt = self.PODCAST_PROMPT.format(
            title=title,
            content=content[:8000],  # Limit content length for context window
            target_length=target_length
        )
        
        return self._generate(prompt)
    
    def _generate(self, prompt: str) -> str:
        """Generate text using Ollama"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Generating content...", total=None)
                
                response = ollama.generate(
                    model=self.model,
                    prompt=prompt,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                )
                
            result = response['response'].strip()
            console.print("[green]✓ Content generated successfully[/green]")
            return result
            
        except Exception as e:
            console.print(f"[red]✗ Generation failed: {e}[/red]")
            raise


def summarize_content(content: str, title: str = "", model: str = None) -> str:
    """Convenience function to summarize content"""
    summarizer = ContentSummarizer(model=model)
    return summarizer.summarize(content, title)


def create_podcast_script(content: str, title: str = "", model: str = None) -> str:
    """Convenience function to create podcast script"""
    summarizer = ContentSummarizer(model=model)
    return summarizer.create_podcast_script(content, title)


if __name__ == "__main__":
    # Test the summarizer
    test_content = """
    Artificial intelligence is transforming every industry. From healthcare to finance,
    AI systems are being deployed to automate tasks, analyze data, and make predictions.
    Machine learning models can now diagnose diseases, detect fraud, and even create art.
    However, these advances come with challenges around ethics, bias, and job displacement.
    """
    
    script = create_podcast_script(test_content, "The AI Revolution")
    print(f"\nPodcast Script:\n{script}")
