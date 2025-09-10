"""
Human behavior simulation for realistic browser interactions.

This module implements realistic human-like browsing patterns including:
- Mouse movement and clicking patterns
- Scroll behavior simulation  
- Typing delays and patterns
- Page interaction timing
"""

import asyncio
import random
import logging
import math
from typing import Tuple, List, Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class BehaviorSimulator:
    """Simulates realistic human browsing behavior"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Human timing patterns (in milliseconds)
        self.typing_delay_range = (50, 200)  # Delay between keystrokes
        self.click_delay_range = (100, 500)  # Delay before clicking
        self.scroll_delay_range = (1000, 3000)  # Delay between scrolls
        self.page_read_time_range = (2000, 8000)  # Time to "read" page content
        
    async def human_type(self, page: Page, selector: str, text: str, 
                        clear_first: bool = True) -> None:
        """Type text with human-like delays and patterns"""
        
        try:
            element = await page.wait_for_selector(selector, timeout=10000)
            
            if clear_first:
                await element.clear()
                await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Focus on the element with a slight delay
            await element.click()
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Type each character with realistic delays
            for i, char in enumerate(text):
                await element.type(char)
                
                # Longer pause for spaces and punctuation
                if char in ' .,;:!?':
                    delay = random.uniform(0.2, 0.4)
                else:
                    delay = random.uniform(0.05, 0.15)
                    
                # Occasional longer pauses (thinking)
                if random.random() < 0.1:
                    delay += random.uniform(0.3, 0.8)
                    
                await asyncio.sleep(delay)
            
            self.logger.debug(f"Human-typed text into {selector}")
            
        except Exception as e:
            self.logger.error(f"Failed to human-type into {selector}: {e}")
            # Fallback to regular typing
            await page.fill(selector, text)
    
    async def human_click(self, page: Page, selector: str, 
                         delay_before: bool = True) -> None:
        """Click element with human-like mouse movement and timing"""
        
        try:
            if delay_before:
                await asyncio.sleep(random.uniform(0.3, 1.0))
            
            element = await page.wait_for_selector(selector, timeout=10000)
            
            # Get element position and size for realistic clicking
            box = await element.bounding_box()
            if box:
                # Click at a random position within the element (not center)
                click_x = box['x'] + random.uniform(0.2, 0.8) * box['width']
                click_y = box['y'] + random.uniform(0.2, 0.8) * box['height']
                
                # Simulate mouse movement to the element
                await self._simulate_mouse_movement(page, click_x, click_y)
                
                # Small delay before clicking
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Click at the calculated position
                await page.mouse.click(click_x, click_y)
            else:
                # Fallback to element click
                await element.click()
            
            # Brief pause after clicking
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            self.logger.debug(f"Human-clicked {selector}")
            
        except Exception as e:
            self.logger.error(f"Failed to human-click {selector}: {e}")
            # Fallback to regular click
            await page.click(selector)
    
    async def human_scroll(self, page: Page, scroll_type: str = 'down', 
                          amount: Optional[int] = None) -> None:
        """Scroll page with human-like patterns"""
        
        try:
            viewport = await page.viewport_size()
            
            if amount is None:
                # Random scroll amount (1-3 screen heights)
                amount = random.randint(int(viewport['height'] * 0.3), 
                                      int(viewport['height'] * 1.5))
            
            # Determine scroll direction
            scroll_delta = amount if scroll_type == 'down' else -amount
            
            # Scroll in smaller increments to simulate wheel scrolling
            increments = random.randint(3, 8)
            increment_size = scroll_delta / increments
            
            for i in range(increments):
                await page.mouse.wheel(0, increment_size)
                
                # Variable delay between scroll increments
                delay = random.uniform(0.1, 0.3)
                if i == 0 or i == increments - 1:
                    delay += random.uniform(0.2, 0.5)  # Longer pause at start/end
                    
                await asyncio.sleep(delay)
            
            # Pause after scrolling (reading time)
            await asyncio.sleep(random.uniform(1.0, 3.0))
            
            self.logger.debug(f"Human-scrolled {scroll_type} by {amount}px")
            
        except Exception as e:
            self.logger.error(f"Failed to human-scroll: {e}")
    
    async def simulate_page_reading(self, page: Page, 
                                   min_time: float = 2.0, 
                                   max_time: float = 8.0) -> None:
        """Simulate reading page content with realistic patterns"""
        
        try:
            # Random reading time
            read_time = random.uniform(min_time, max_time)
            
            # Break reading into segments with occasional scrolls
            segments = random.randint(2, 5)
            segment_time = read_time / segments
            
            for i in range(segments):
                # Reading pause
                await asyncio.sleep(segment_time * random.uniform(0.7, 1.3))
                
                # Occasional scroll while reading
                if random.random() < 0.6 and i < segments - 1:
                    scroll_amount = random.randint(100, 300)
                    await self.human_scroll(page, 'down', scroll_amount)
            
            self.logger.debug(f"Simulated reading for {read_time:.1f}s")
            
        except Exception as e:
            self.logger.error(f"Failed to simulate reading: {e}")
    
    async def simulate_form_interaction(self, page: Page, 
                                       form_data: dict) -> None:
        """Simulate realistic form filling behavior"""
        
        try:
            fields = list(form_data.items())
            random.shuffle(fields)  # Fill fields in random order sometimes
            
            for i, (selector, value) in enumerate(fields):
                # Pause before interacting with field
                if i > 0:
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                
                # Focus and fill the field
                await self.human_click(page, selector)
                await asyncio.sleep(random.uniform(0.2, 0.5))
                await self.human_type(page, selector, str(value))
                
                # Occasional pause (thinking/checking)
                if random.random() < 0.3:
                    await asyncio.sleep(random.uniform(1.0, 3.0))
            
            self.logger.debug("Completed form interaction simulation")
            
        except Exception as e:
            self.logger.error(f"Failed to simulate form interaction: {e}")
    
    async def simulate_navigation_delay(self, page: Page) -> None:
        """Simulate realistic delays during navigation"""
        
        try:
            # Wait for page to load
            await page.wait_for_load_state('domcontentloaded')
            
            # Additional delay for page rendering and reading
            await asyncio.sleep(random.uniform(1.0, 3.0))
            
            # Check if page has loaded content
            try:
                await page.wait_for_load_state('networkidle', timeout=5000)
                await asyncio.sleep(random.uniform(0.5, 1.5))
            except:
                # If networkidle times out, just add a standard delay
                await asyncio.sleep(random.uniform(2.0, 4.0))
            
            self.logger.debug("Completed navigation delay simulation")
            
        except Exception as e:
            self.logger.error(f"Failed to simulate navigation delay: {e}")
    
    async def _simulate_mouse_movement(self, page: Page, 
                                      target_x: float, target_y: float) -> None:
        """Simulate realistic mouse movement to target position"""
        
        try:
            # Get current mouse position (assume starting from random position)
            start_x = random.uniform(100, 500)
            start_y = random.uniform(100, 400)
            
            # Calculate movement steps
            distance = math.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
            steps = max(3, int(distance / 50))  # More steps for longer distances
            
            # Move mouse in steps with slight randomness
            for i in range(steps):
                progress = (i + 1) / steps
                
                # Add some curve to the movement (human-like)
                curve_offset = math.sin(progress * math.pi) * random.uniform(-10, 10)
                
                current_x = start_x + (target_x - start_x) * progress + curve_offset
                current_y = start_y + (target_y - start_y) * progress
                
                await page.mouse.move(current_x, current_y)
                await asyncio.sleep(random.uniform(0.01, 0.05))
            
            # Final position adjustment
            await page.mouse.move(target_x, target_y)
            
        except Exception as e:
            self.logger.error(f"Failed to simulate mouse movement: {e}")
    
    async def random_page_interaction(self, page: Page) -> None:
        """Perform random human-like interactions on the page"""
        
        try:
            # Random interactions
            interactions = [
                self._random_scroll,
                self._random_mouse_movement,
                self._random_pause
            ]
            
            # Perform 1-3 random interactions
            num_interactions = random.randint(1, 3)
            for _ in range(num_interactions):
                interaction = random.choice(interactions)
                await interaction(page)
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            self.logger.debug("Completed random page interaction")
            
        except Exception as e:
            self.logger.error(f"Failed to perform random interaction: {e}")
    
    async def _random_scroll(self, page: Page) -> None:
        """Perform a random scroll action"""
        scroll_type = random.choice(['down', 'up'])
        await self.human_scroll(page, scroll_type)
    
    async def _random_mouse_movement(self, page: Page) -> None:
        """Perform random mouse movement"""
        viewport = await page.viewport_size()
        x = random.uniform(100, viewport['width'] - 100)
        y = random.uniform(100, viewport['height'] - 100)
        await self._simulate_mouse_movement(page, x, y)
    
    async def _random_pause(self, page: Page) -> None:
        """Random pause (simulating reading/thinking)"""
        await asyncio.sleep(random.uniform(1.0, 4.0))
