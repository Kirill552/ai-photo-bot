"""
Prompt generation module
"""

import logging
from typing import List, Dict, Any
import random

logger = logging.getLogger(__name__)


class PromptGenerator:
    """Generate prompts based on client brief"""
    
    def __init__(self):
        # Style templates with professional prompts (updated 2025)
        self.style_templates = {
            "RL-01": {
                "name": "Realistic Studio Vogue",
                "base": "/Imagine a cinematic studio portrait of a young person, softbox key light, pastel seamless background, gentle color grading, shot on Phase One IQ4 150 MP, ultra-realistic skin texture, fashion-editorial mood --ar 3:4",
                "variations": [
                    "confident gaze, elegant pose",
                    "subtle smile, fashion styling", 
                    "intense lighting, dramatic shadows",
                    "glamour makeup, perfect retouching"
                ],
                "lora_type": "realism"
            },
            "FN-02": {
                "name": "Fantasy Ethereal", 
                "base": "/Imagine a young person as ethereal forest fairy, backlit by golden dust particles, pastel haze, flowing chiffon dress, fantasy artbook quality, volumetric lighting, 8k RAW --ar 2:3",
                "variations": [
                    "flowing hair, dreamy expression",
                    "delicate flowers, soft textures",
                    "morning light, romantic mood",
                    "vintage aesthetics, warm tones"
                ],
                "lora_type": "realism"
            },
            "CP-03": {
                "name": "Cyberpunk Neon City",
                "base": "/Imagine a cyberpunk portrait of a young person, neon Tokyo alley, rain-soaked jacket, reflective puddles, teal-magenta color scheme, cinematic DOF, 50 mm f/1.2, ultra-realistic --ar 3:4",
                "variations": [
                    "with neon lights and urban atmosphere",
                    "with futuristic styling and tech elements",
                    "with rain effects and reflections",
                    "with cyberpunk aesthetics and glow"
                ],
                "lora_type": "graphic-portrait"
            },
            "MJ6-04": {
                "name": "Midjourney V6 Look",
                "base": "/Imagine an elegant editorial portrait of a young person, soft rim light, minimal background, Vogue aesthetic, hyper-detail --ar 3:4",
                "variations": [
                    "with magazine-quality perfection",
                    "with editorial styling and composition",
                    "with hyper-realistic details",
                    "with premium fashion aesthetics"
                ],
                "lora_type": "mjv6",
                "lora_strength": 0.8
            },
            "CEO-05": {
                "name": "Corporate Headshot",
                "base": "/Imagine a professional corporate headshot of a young person, charcoal blazer, subtle rim light, dark grey backdrop, Leica SL2-S 90 mm Summicron prime lens, impeccable skin retouch, Forbes cover mood --ar 4:5",
                "variations": [
                    "with professional confidence and direct gaze",
                    "with subtle smile and business attire",
                    "with executive presence and clean styling",
                    "with leadership aura and polished look"
                ],
                "lora_type": "realism"
            },
            "PST-06": {
                "name": "Pastel Dream",
                "base": "/Imagine a young person in pastel dream aesthetic, diffused window light, blooming peonies, mint & blush palette, Fuji Pro400H film simulation, light grain, shallow DOF 1.2, 85 mm lens --ar 2:3",
                "variations": [
                    "with soft pastel colors and dreamy atmosphere",
                    "with delicate flowers and textures",
                    "with romantic mood and film emulation",
                    "with vintage aesthetics and warm tones"
                ],
                "lora_type": "realism"
            },
            "CLS-07": {
                "name": "Classic B&W",
                "base": "/Imagine a timeless black-and-white portrait of a young person, high-contrast Rembrandt lighting, medium-format Hasselblad, deep shadows, Ilford HP5 film emulation, 6k resolution --ar 1:1",
                "variations": [
                    "with dramatic lighting and classic elegance",
                    "with timeless beauty and sophisticated styling",
                    "with artistic shadows and monochrome aesthetics",
                    "with vintage Hollywood glamour"
                ],
                "lora_type": "realism"
            },
            "CSP-08": {
                "name": "Cosplay Hero",
                "base": "/Imagine a young person as heroic fantasy warrior, ornate armor with glowing runes, dynamic rim light, dramatic atmosphere, concept-art quality, epic scale --ar 3:4",
                "variations": [
                    "with fantasy armor and heroic pose",
                    "with magical elements and epic lighting",
                    "with warrior aesthetics and power",
                    "with concept art quality and details"
                ],
                "lora_type": "graphic-portrait"
            }
        }
        
        self.background_options = {
            "studio": "studio seamless white backdrop",
            "pastel": "soft pastel seamless background",
            "urban": "urban brick wall background",
            "nature": "natural outdoor setting",
            "minimal": "clean minimal background",
            "textured": "textured studio backdrop",
            "gradient": "gradient colored background"
        }
        
        self.mood_modifiers = {
            "confident": "confident and empowered expression",
            "soft": "soft and gentle demeanor",
            "dramatic": "dramatic and intense mood",
            "playful": "playful and vibrant energy",
            "elegant": "elegant and sophisticated presence",
            "natural": "natural and relaxed atmosphere"
        }
    
    def generate_prompts(self, brief: Dict[str, Any]) -> List[str]:
        """Generate prompts based on brief"""
        
        style = brief.get("style", "RL-01")
        background = brief.get("background", "studio backdrop")
        package = brief.get("package", 40)  # Still support old format
        package_type = brief.get("package_type", self._get_package_type(package))
        
        # Determine number of prompts needed
        num_prompts = self._get_prompt_count_by_package(package_type)
        
        prompts = []
        template = self.style_templates.get(style, self.style_templates["RL-01"])
        
        # Process background
        background_desc = self._process_background(background)
        
        for i in range(num_prompts):
            base_prompt = template["base"].format(background=background_desc)
            
            # Add variation if available
            if i < len(template["variations"]):
                variation = template["variations"][i]
                prompt = f"{base_prompt}, {variation}"
            else:
                # Use mood modifiers for extra variations
                mood = list(self.mood_modifiers.values())[i % len(self.mood_modifiers)]
                prompt = f"{base_prompt}, {mood}"
            
            # Add purpose-specific modifiers
            purpose = brief.get("purpose", "insta")
            prompt = self._add_purpose_modifiers(prompt, purpose)
            
            # Add LoRA settings if needed
            if template.get("lora_type"):
                lora_strength = template.get("lora_strength", 0.7)
                prompt += f" <lora_type:\"{template['lora_type']}\", lora_strength:{lora_strength}>"
            
            prompts.append(prompt)
        
        return prompts
    
    def _get_prompt_count(self, package: int) -> int:
        """Determine number of prompt variations based on package"""
        
        if package <= 40:
            return 10  # 10 prompts × 4 images each = 40 images
        elif package <= 60:
            return 12  # 12 prompts × 5 images each = 60 images
        elif package <= 80:
            return 16  # 16 prompts × 5 images each = 80 images
        else:
            return 20  # 20 prompts × 5 images each = 100 images
    
    def _process_background(self, background: str) -> str:
        """Process background description"""
        
        # If it's a predefined background type
        if background.lower() in self.background_options:
            return self.background_options[background.lower()]
        
        # If it's a custom description
        if len(background) > 5:
            return f"background: {background}"
        
        # Default background
        return self.background_options["studio"]
    
    def _add_purpose_modifiers(self, prompt: str, purpose: str) -> str:
        """Add purpose-specific modifiers to prompt"""
        
        modifiers = {
            "insta": "instagram-ready, social media optimized",
            "avatar": "profile picture perfect, clean and professional",
            "career": "professional and polished, LinkedIn ready",
            "dating": "attractive and approachable, confident smile"
        }
        
        if purpose in modifiers:
            prompt += f", {modifiers[purpose]}"
        
        return prompt
    
    def _generate_cross_style_prompts(self, brief: Dict[str, Any]) -> List[str]:
        """Generate cross-style prompts for premium packages"""
        
        try:
            current_style = brief.get("style", "Studio Vogue")
            background = brief.get("background", "studio backdrop")
            
            # Get 2-3 different styles
            other_styles = [style for style in self.style_templates.keys() if style != current_style]
            selected_styles = random.sample(other_styles, min(3, len(other_styles)))
            
            cross_prompts = []
            for style in selected_styles:
                template = self.style_templates[style]
                background_desc = self._process_background(background)
                
                # Generate 2-3 prompts per style
                for i in range(2):
                    base_prompt = template["base"].format(background=background_desc)
                    if i < len(template["variations"]):
                        variation = template["variations"][i]
                        prompt = f"{base_prompt} {variation}"
                    else:
                        mood = random.choice(list(self.mood_modifiers.values()))
                        prompt = f"{base_prompt} {mood}"
                    
                    cross_prompts.append(prompt)
            
            logger.info(f"Generated {len(cross_prompts)} cross-style prompts")
            return cross_prompts
            
        except Exception as e:
            logger.error(f"Error generating cross-style prompts: {e}")
            return []
    
    def _get_fallback_prompts(self, brief: Dict[str, Any]) -> List[str]:
        """Get fallback prompts in case of error"""
        
        package = brief.get("package", 40)
        count = self._get_prompt_count(package)
        
        fallback_prompts = [
            "/Imagine a professional portrait of a young person, studio lighting, clean background, high quality, 8k resolution --ar 3:4",
            "/Imagine a beautiful headshot of a young person, soft lighting, elegant pose, professional photography --ar 3:4",
            "/Imagine a stylish portrait of a young person, modern aesthetic, crisp details, magazine quality --ar 3:4",
            "/Imagine a confident portrait of a young person, natural lighting, professional style, ultra-realistic --ar 3:4",
            "/Imagine an elegant portrait of a young person, studio setup, polished look, high-end photography --ar 3:4"
        ]
        
        # Repeat fallback prompts to reach desired count
        prompts = []
        for i in range(count):
            prompt_index = i % len(fallback_prompts)
            prompts.append(fallback_prompts[prompt_index])
        
        logger.warning(f"Using {len(prompts)} fallback prompts")
        return prompts
    
    def validate_prompt(self, prompt: str) -> bool:
        """Validate prompt for content policy"""
        
        # Check for forbidden words/phrases
        forbidden_words = [
            "nude", "naked", "nsfw", "sexual", "explicit",
            "inappropriate", "adult", "xxx", "porn"
        ]
        
        prompt_lower = prompt.lower()
        for word in forbidden_words:
            if word in prompt_lower:
                logger.warning(f"Prompt contains forbidden word: {word}")
                return False
        
        # Check minimum length
        if len(prompt) < 10:
            logger.warning("Prompt too short")
            return False
        
        # Check maximum length
        if len(prompt) > 1000:
            logger.warning("Prompt too long")
            return False
        
        return True
    
    def get_style_preview(self, style: str) -> str:
        """Get style preview description"""
        
        descriptions = {
            "RL-01": "Realistic Studio Vogue - драматичное студийное освещение, как в глянцевых журналах",
            "FN-02": "Fantasy Ethereal - сказочная атмосфера с волшебными эффектами",
            "CP-03": "Cyberpunk Neon City - футуристический киберпанк с неоновыми огнями",
            "MJ6-04": "Midjourney V6 Look - премиальная обработка в стиле Midjourney",
            "CEO-05": "Corporate Headshot - деловые портреты для LinkedIn и резюме",
            "PST-06": "Pastel Dream - нежные пастельные тона, воздушная атмосфера",
            "CLS-07": "Classic B&W - классическая черно-белая фотография",
            "CSP-08": "Cosplay Hero - героические образы в стиле фэнтези"
        }
        
        return descriptions.get(style, "Профессиональная фотография")
    
    def _get_package_type(self, package: int) -> str:
        """Convert old package format to new package type"""
        
        if package <= 2:
            return "trial"
        elif package <= 10:
            return "basic"
        elif package <= 25:
            return "standard"
        else:
            return "premium"
    
    def _get_prompt_count_by_package(self, package_type: str) -> int:
        """Get number of prompts needed for package type"""
        
        package_counts = {
            "trial": 2,      # 2 фото
            "basic": 5,      # 10 фото (5 prompts × 2 images)
            "standard": 12,  # 25 фото (12 prompts × 2 images)
            "premium": 25    # 50 фото (25 prompts × 2 images)
        }
        
        return package_counts.get(package_type, 5)
    
    def get_package_info(self, package_type: str) -> Dict[str, Any]:
        """Get package information"""
        
        packages = {
            "trial": {
                "name": "Пробный",
                "photos": 2,
                "styles": 1,
                "video": False,
                "post_process": False,
                "price": 0
            },
            "basic": {
                "name": "Базовый", 
                "photos": 10,
                "styles": 3,
                "video": False,
                "post_process": False,
                "price": 1500
            },
            "standard": {
                "name": "Стандарт",
                "photos": 25,
                "styles": 5,
                "video": True,
                "post_process": False,
                "price": 3500
            },
            "premium": {
                "name": "Премиум",
                "photos": 50,
                "styles": 8,
                "video": True,
                "post_process": True,
                "price": 8990
            }
        }
        
        return packages.get(package_type, packages["basic"])
    
    def get_style_code(self, style: str) -> str:
        """Get style code for video generation"""
        
        template = self.style_templates.get(style, {})
        return template.get("lora_type", "realism")
    
    def get_all_styles(self) -> Dict[str, str]:
        """Get all available styles with their names"""
        
        styles = {}
        for code, template in self.style_templates.items():
            styles[code] = template.get("name", code)
        
        return styles
    
    def get_popular_styles(self) -> List[str]:
        """Get most popular styles according to plan"""
        
        # Based on section 19.2 of the plan
        return ["RL-01", "FN-02", "CEO-05", "PST-06", "CLS-07", "CP-03"] 