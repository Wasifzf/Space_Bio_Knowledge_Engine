def synthesize_answer(self, query: str, vector_context: List[Dict], kg_context: Dict) -> str:
    """Use Groq to synthesize information from both sources with conversation memory"""
    
    # Build conversation context
    conversation_context = self.get_conversation_context()
    
    # Build structured context (vector excerpts + KG answer + minimal provenance)
    parts: List[str] = []
    
    # Add conversation context if available
    if conversation_context:
        parts.append(conversation_context)
        
    if kg_context.get('relevant_triples_count', 0) > 0:
        parts.append("[Knowledge Graph Answer]\n" + kg_context.get('answer', '')[:3000])
        # Optionally include a compact list of top triples
        top_triples = kg_context.get('top_triples') or []
        if top_triples:
            triple_lines = []
            for t in top_triples[:8]:
                triple_lines.append(f"- {t.get('subject')} --{t.get('predicate')}--> {t.get('object')} ({int(t.get('confidence', 0)*100)}%)")
            parts.append("[Representative Relationships]\n" + "\n".join(triple_lines))
    if vector_context:
        paper_lines = []
        for i, doc in enumerate(vector_context[:5], 1):
            snippet = (doc.get('text') or '')[:300].replace('\n', ' ')
            title = doc.get('title', 'Unknown Title')
            year = doc.get('year', 'Unknown')
            paper_lines.append(f"{i}. {title} ({year}) - {snippet}...")
        parts.append("[Vector Retrieved Excerpts]\n" + "\n".join(paper_lines))
    context = "\n\n".join(parts) if parts else "No additional context retrieved."

    try:
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Groq-supported model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly and knowledgeable AI assistant specialized in space biology research. "
                        "You can handle both casual conversations and in-depth scientific discussions. "
                        "Respond appropriately based on the query type:\n\n"
                        "**For simple greetings or casual queries (like 'hi', 'hello', 'how are you', 'thanks'):**\n"
                        "- Respond warmly and naturally\n"
                        "- Introduce yourself as a space biology research assistant\n"
                        "- Offer to help with specific topics like microgravity effects, space organisms, astronaut health, etc.\n"
                        "- Keep it brief and friendly\n"
                        "- Don't overwhelm with technical details\n\n"
                        "**For scientific research questions:**\n"
                        "Format your response with clear structure using markdown-style formatting:\n"
                        "1. Start with a clear, bold **summary statement**\n"
                        "2. Use **bold headers** for main sections (e.g., **Key Mechanisms**, **Research Findings**)\n" 
                        "3. Use bullet points (•) for listing multiple related items\n"
                        "4. Use numbered lists (1., 2., 3.) for sequential processes or prioritized information\n"
                        "5. Include **bold emphasis** for important terms and concepts\n"
                        "6. End with a **Conclusion** section that synthesizes the main points\n\n"
                        "Scientific requirements:\n"
                        "- Reference previous conversation when relevant for continuity\n"
                        "- Integrate findings across all sources, identifying consensus and key experiments\n"
                        "- Emphasize scientific reasoning and mechanisms\n"
                        "- Maintain professional but engaging tone\n"
                        "- Highlight knowledge gaps where relevant\n"
                        "- Ensure the response flows naturally like a literature review\n\n"
                        "DO NOT include citations in the main text - they will be added separately as clickable links."
                    )
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nCurrent Question: {query}"
                }
            ],
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"⚠️ Answer synthesis failed: {e}")
        
        # Enhanced fallback response with formatting
        fallback = "**Research Summary:**\n\n"
        if kg_context.get('answer'):
            fallback += kg_context['answer'] + "\n\n"
        
        if vector_context:
            fallback += "**Additional Research Context:**\n"
            for i, doc in enumerate(vector_context[:2], 1):
                fallback += f"{i}. {doc.get('text', '')[:150]}...\n"
            
            # Add sources
            fallback += "\n**📚 Sources:**\n"
            for i, doc in enumerate(vector_context[:2], 1):
                title = doc.get('title', 'Unknown Title')
                year = doc.get('year', '')
                doi = doc.get('doi', '')
                source_text = f"{i}. **{title}** ({year})"
                if doi:
                    source_text += f" - [DOI: {doi}](https://doi.org/{doi})"
                fallback += source_text + "\n"
        
        return fallback