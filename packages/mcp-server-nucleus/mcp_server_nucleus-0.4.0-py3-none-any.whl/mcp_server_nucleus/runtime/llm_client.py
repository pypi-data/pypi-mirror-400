"""
Dual-Engine LLM Client for Nucleus
Implements a fallback strategy to transition from google.generativeai (Legacy) to google.genai (New).

MDR_010 Compliant: Ensures high availability and reliability.
"""

import os
import logging

logger = logging.getLogger("nucleus.llm")

class DualEngineLLM:
    def __init__(self, model_name="gemini-2.0-flash-exp", system_instruction=None, api_key=None):
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        self.legacy_model = None
        self.engine = "UNKNOWN"
        
        # Initialize Engines
        self._init_new_engine()
        
    def _init_new_engine(self):
        """Attempt to initialize the new google.genai Client"""
        try:
            from google import genai
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found")
                
            self.client = genai.Client(api_key=self.api_key, http_options={'api_version': 'v1alpha'})
            self.engine = "NEW"
            logger.info("✅ LLM Client: Initialized NEW engine (google.genai)")
        except ImportError:
            logger.warning("⚠️ LLM Client: google.genai not installed. Falling back.")
            self.engine = "LEGACY"
        except Exception as e:
            logger.warning(f"⚠️ LLM Client: New engine init failed ({e}). Falling back.")
            self.engine = "LEGACY"

    def _init_legacy_engine(self):
        """Lazy init for legacy engine"""
        if self.legacy_model:
            return
            
        try:
            import google.generativeai as old_genai
            # Use instance key if available, else env
            api_key = self.api_key or os.environ.get("GEMINI_API_KEY")
            old_genai.configure(api_key=api_key)
            
            # Handle system_instruction compatibility safely
            model_kwargs = {}
            if self.system_instruction:
                model_kwargs['system_instruction'] = self.system_instruction
                
            try:
                self.legacy_model = old_genai.GenerativeModel(
                    self.model_name,
                    **model_kwargs
                )
            except TypeError:
                 # Fallback for older SDKs that don't support system_instruction arg
                 logger.warning("⚠️ LLM Client: Legacy SDK does not support system_instruction. ignoring.")
                 self.legacy_model = old_genai.GenerativeModel(self.model_name)
            logger.info("⚠️ LLM Client: Initialized LEGACY engine (google.generativeai)")
        except Exception as e:
            logger.error(f"❌ LLM Client: Legacy engine init failed: {e}")
            raise

    def generate_content(self, prompt, **kwargs):
        """
        Generate content using the active engine.
        Automatically falls back to legacy if new engine fails.
        """
        # CRITICAL: Force Legacy Engine if tools involved (Gradual Rollout)
        # The new Google GenAI SDK handles tools differently (config=...).
        # To avoid breaking existing tool definitions, we route tool calls to Legacy.
        # This allows us to migrate SIMPLE calls first, and complex tools later.
        if any(k in kwargs for k in ["tools", "tool_config", "functions"]):
            logger.info("ℹ️ LLM Client: Tools detected. Forcing LEGACY engine for compatibility.")
            self.engine = "LEGACY"

        # Force Legacy Engine if tools involved (Gradual Rollout)
        # The new Google GenAI SDK handles tools differently (config=...).
        # To avoid breaking existing tool definitions, we route tool calls to Legacy.
        if any(k in kwargs for k in ["tools", "tool_config", "functions"]):
            logger.info("ℹ️ LLM Client: Tools detected. Forcing LEGACY engine for compatibility.")
            self.engine = "LEGACY"

        if self.engine == "NEW":
            try:
                # Map kwargs if necessary (e.g. generation_config)
                # The new API config structure is slightly different, but basic usage is similar.
                # For safety, we strip unknown kwargs that might be legacy-specific for now,
                # or wrap them carefully.
                
                # Basic call
                config = {}
                if self.system_instruction:
                    config['system_instruction'] = self.system_instruction
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                return response
            except Exception as e:
                logger.warning(f"⚠️ LLM Client: New engine runtime error: {e}. Switching to legacy.")
                self.engine = "LEGACY"
                # Fallthrough to legacy logic below
        
        # Legacy Fallback
        self._init_legacy_engine()
        
        # FIX: google-generativeai requires tools in constructor for some versions
        if "tools" in kwargs:
            try:
                import google.generativeai as old_genai
                
                # Prepare constructor args
                init_kwargs = {}
                if self.system_instruction:
                    init_kwargs['system_instruction'] = self.system_instruction
                
                # Instantiate temporary model with tools
                try:
                    temp_model = old_genai.GenerativeModel(
                        self.model_name,
                        tools=kwargs['tools'],
                        **init_kwargs
                    )
                except TypeError:
                    # Retry without system_instruction (if that was the cause)
                    if 'system_instruction' in init_kwargs:
                        init_kwargs.pop('system_instruction')
                        temp_model = old_genai.GenerativeModel(
                            self.model_name,
                            tools=kwargs['tools'],
                            **init_kwargs
                        )
                    else:
                        raise
                
                # Remove tools from kwargs to avoid "multiple values" error
                run_kwargs = {k: v for k, v in kwargs.items() if k != 'tools'}
                
                return temp_model.generate_content(prompt, **run_kwargs)
            except Exception as e:
                logger.warning(f"⚠️ LLM Client: Temp model creation failed: {e}. Trying standard path.")
                # Fall through to standard path
        
        return self.legacy_model.generate_content(prompt, **kwargs)

    def embed_content(self, text, task_type="retrieval_document", title=None):
        """
        Generate embeddings using the active engine.
        Args:
            text: Content to embed
            task_type: retrieval_document | retrieval_query | etc
            title: Optional title (required for retrieval_document in some models)
        """
        # Determine engine (default to NEW if initialized)
        if self.engine == "UNKNOWN":
             self._init_new_engine()
             
        if self.engine == "NEW":
            try:
                # New SDK: client.models.embed_content
                # args: model, contents, config(task_type, title)
                config = {'task_type': task_type.replace("retrieval_", "RETRIEVAL_").upper()} # e.g. RETRIEVAL_DOCUMENT
                if title:
                    config['title'] = title
                
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=text,
                    config=config
                )
                
                # Normalize output (New SDK likely returns object with embedding attribute)
                # Check response structure. Usually response.embeddings[0].values
                if hasattr(response, 'embeddings') and response.embeddings:
                    return {'embedding': response.embeddings[0].values}
                return {'embedding': []} # Fallback
                
            except Exception as e:
                logger.warning(f"⚠️ LLM Client: New engine embedding failed: {e}. Switching to legacy.")
                self.engine = "LEGACY"

        # Legacy Fallback
        self._init_legacy_engine()
        
        try:
            import google.generativeai as old_genai
            # Legacy: genai.embed_content(model, content, task_type, title)
            return old_genai.embed_content(
                model=self.model_name,
                content=text,
                task_type=task_type,
                title=title
            )
        except Exception as e:
            logger.error(f"❌ LLM Client: Legacy embedding failed: {e}")
            raise

    @property
    def active_engine(self):
        return self.engine
