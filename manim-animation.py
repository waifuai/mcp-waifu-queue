from manim import *

class MCPWaifuQueueExplanation(Scene):
    def construct(self):
        # Scene 1: Introduction
        title = Text("MCP Waifu Queue", font_size=48, color=BLUE)
        subtitle = Text("Conversational AI with Redis Queue", font_size=32, color=WHITE)
        description = Text(
            "An MCP server for AI text generation using Redis for async processing.",
            font_size=24, color=LIGHT_GRAY
        ).next_to(subtitle, DOWN)
        title.move_to(UP*3)
        self.play(Write(title))
        self.play(Write(subtitle))
        self.play(FadeIn(description))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(description))

        # Scene 2: Architecture Overview
        # Create component boxes
        client = Rectangle(width=2, height=0.8, color=GREEN).shift(LEFT * 4 + UP * 2)
        client_label = Text("Client", font_size=20).move_to(client.get_center())

        main_py = Rectangle(width=2.5, height=0.8, color=BLUE).next_to(client, RIGHT, buff=1)
        main_label = Text("main.py\n(MCP Server)", font_size=16).move_to(main_py.get_center())

        redis = Rectangle(width=2, height=0.8, color=RED).next_to(main_py, RIGHT, buff=1)
        redis_label = Text("Redis Queue", font_size=16).move_to(redis.get_center())

        worker = Rectangle(width=2.5, height=0.8, color=ORANGE).next_to(redis, RIGHT, buff=1)
        worker_label = Text("worker.py\n(RQ Worker)", font_size=16).move_to(worker.get_center())

        respond = Rectangle(width=2.5, height=0.8, color=PURPLE).next_to(worker, DOWN, buff=1.5)
        respond_label = Text("respond.py\n(Text Gen)", font_size=16).move_to(respond.get_center())

        providers = Rectangle(width=3, height=0.8, color=YELLOW).next_to(respond, DOWN, buff=1.5)
        providers_label = Text("Providers\n(OpenRouter/Gemini)", font_size=16).move_to(providers.get_center())

        # Arrows for flow
        arrow1 = Arrow(client.get_right(), main_py.get_left(), color=WHITE)
        arrow2 = Arrow(main_py.get_right(), redis.get_left(), color=WHITE)
        arrow3 = Arrow(redis.get_right(), worker.get_left(), color=WHITE)
        arrow4 = Arrow(worker.get_bottom(), respond.get_top(), color=WHITE)
        arrow5 = Arrow(respond.get_bottom(), providers.get_top(), color=WHITE)

        # Add to scene
        components = VGroup(client, main_py, redis, worker, respond, providers)
        labels = VGroup(client_label, main_label, redis_label, worker_label, respond_label, providers_label)
        arrows = VGroup(arrow1, arrow2, arrow3, arrow4, arrow5)

        self.play(Create(components), Write(labels))
        self.play(Create(arrows))
        self.wait(3)

        # Scene 3: Request Flow Animation
        # Animate flow with moving text
        prompt_text = Text("Prompt", font_size=18, color=GREEN).move_to(client.get_center())
        self.play(Write(prompt_text))
        self.play(prompt_text.animate.move_to(main_py.get_center()))
        self.play(prompt_text.animate.move_to(redis.get_center()))
        self.play(prompt_text.animate.move_to(worker.get_center()))
        self.play(prompt_text.animate.move_to(respond.get_center()))
        self.play(prompt_text.animate.move_to(providers.get_center()))
        self.play(FadeOut(prompt_text))

        result_text = Text("Result", font_size=18, color=BLUE).move_to(providers.get_center())
        self.play(Write(result_text))
        self.play(result_text.animate.move_to(redis.get_center()))
        self.play(FadeOut(result_text))

        # Scene 4: Providers Explanation
        self.play(components.animate.set_opacity(0.3), labels.animate.set_opacity(0.3), arrows.animate.set_opacity(0.3))
        openrouter = Rectangle(width=2, height=0.6, color=TEAL).next_to(providers, LEFT, buff=0.5)
        openrouter_label = Text("OpenRouter\n(Default)", font_size=16).move_to(openrouter.get_center())
        gemini = Rectangle(width=2, height=0.6, color=PURPLE).next_to(providers, RIGHT, buff=0.5)
        gemini_label = Text("Gemini\n(Fallback)", font_size=16).move_to(gemini.get_center())

        provider_text = Text("API Key: env or ~/.api-* files", font_size=20, color=WHITE).next_to(providers, DOWN)
        self.play(Create(openrouter), Write(openrouter_label), Create(gemini), Write(gemini_label), Write(provider_text))
        self.wait(2)
        self.play(FadeOut(openrouter), FadeOut(openrouter_label), FadeOut(gemini), FadeOut(gemini_label), FadeOut(provider_text))

        # Scene 5: Configuration
        config_text = Text("Configuration via .env", font_size=24, color=WHITE).shift(UP)
        config_items = VGroup(
            Text("• MAX_NEW_TOKENS", font_size=18),
            Text("• REDIS_URL", font_size=18),
            Text("• PROVIDER (openrouter/gemini)", font_size=18),
            Text("• API Keys from env or files", font_size=18)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(config_text, DOWN)

        self.play(Write(config_text), Write(config_items))
        self.wait(2)
        self.play(FadeOut(config_text), FadeOut(config_items))

        # Scene 6: Conclusion
        conclusion = Text("Efficient Async AI Processing with MCP and Redis", font_size=32, color=GOLD)
        self.play(Write(conclusion))
        self.wait(2)
        self.play(FadeOut(conclusion), FadeOut(components), FadeOut(labels), FadeOut(arrows))