import React from 'react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = "" }) => {
  const renderMarkdown = (text: string) => {
    const lines = text.split('\n');
    const result: React.ReactNode[] = [];
    let currentParagraph: string[] = [];
    let inList = false;
    let listItems: string[] = [];

    const flushParagraph = () => {
      if (currentParagraph.length > 0) {
        const paragraphText = currentParagraph.join(' ');
        result.push(
          <p key={`p-${result.length}`} className="mb-3 leading-relaxed">
            {renderInlineFormatting(paragraphText)}
          </p>
        );
        currentParagraph = [];
      }
    };

    const flushList = () => {
      if (listItems.length > 0) {
        result.push(
          <ul key={`ul-${result.length}`} className="mb-4 ml-4 space-y-2">
            {listItems.map((item, idx) => (
              <li key={idx} className="list-disc">
                {renderInlineFormatting(item)}
              </li>
            ))}
          </ul>
        );
        listItems = [];
        inList = false;
      }
    };

    lines.forEach((line, index) => {
      const trimmedLine = line.trim();

      // Handle headers
      if (trimmedLine.startsWith('**') && trimmedLine.endsWith('**') && trimmedLine.includes(':')) {
        flushParagraph();
        flushList();
        const headerText = trimmedLine.slice(2, -2);
        result.push(
          <h3 key={`h-${result.length}`} className="text-lg font-bold text-gray-800 mt-6 mb-3">
            {headerText}
          </h3>
        );
        return;
      }

      // Handle bullet points
      if (trimmedLine.startsWith('•') || trimmedLine.match(/^\d+\./)) {
        flushParagraph();
        if (!inList) {
          inList = true;
        }
        const itemText = trimmedLine.replace(/^[•\d+\.]\s*/, '');
        listItems.push(itemText);
        return;
      }

      // Handle empty lines
      if (trimmedLine === '') {
        flushParagraph();
        flushList();
        return;
      }

      // Regular paragraph content
      flushList();
      currentParagraph.push(trimmedLine);
    });

    // Flush remaining content
    flushParagraph();
    flushList();

    return result;
  };

  const renderInlineFormatting = (text: string): React.ReactNode[] => {
    const parts: React.ReactNode[] = [];
    let currentIndex = 0;

    // Handle bold text **text**
    const boldRegex = /\*\*(.*?)\*\*/g;
    let match;

    while ((match = boldRegex.exec(text)) !== null) {
      // Add text before the match
      if (match.index > currentIndex) {
        const beforeText = text.slice(currentIndex, match.index);
        parts.push(...renderLinks(beforeText, parts.length));
      }

      // Add bold text
      parts.push(
        <strong key={`bold-${parts.length}`} className="font-semibold text-gray-900">
          {match[1]}
        </strong>
      );

      currentIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (currentIndex < text.length) {
      const remainingText = text.slice(currentIndex);
      parts.push(...renderLinks(remainingText, parts.length));
    }

    return parts;
  };

  const renderLinks = (text: string, startKey: number): React.ReactNode[] => {
    const parts: React.ReactNode[] = [];
    
    // Handle markdown links [text](url)
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let currentIndex = 0;
    let match;
    let keyCounter = startKey;

    while ((match = linkRegex.exec(text)) !== null) {
      // Add text before the link
      if (match.index > currentIndex) {
        parts.push(text.slice(currentIndex, match.index));
      }

      // Add the link
      parts.push(
        <a
          key={`link-${keyCounter++}`}
          href={match[2]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 hover:underline transition-colors"
        >
          {match[1]}
        </a>
      );

      currentIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (currentIndex < text.length) {
      parts.push(text.slice(currentIndex));
    }

    return parts.length > 0 ? parts : [text];
  };

  return (
    <div className={`prose prose-sm max-w-none ${className}`}>
      {renderMarkdown(content)}
    </div>
  );
};

export default MarkdownRenderer;