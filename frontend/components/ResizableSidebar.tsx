import { Summary } from '@/types/discord';
import React, { useCallback, useState } from 'react';

interface Props {
  summaryHistory: Summary[];
  onSelectSummary: (summary: Summary) => void;
  onDeleteSummary: (summary: Summary) => void;
  defaultWidth?: number;
  minWidth?: number;
  maxWidth?: number;
}

export default function ResizableSidebar({ 
  summaryHistory, 
  onSelectSummary,
  onDeleteSummary,
  defaultWidth = 320,
  minWidth = 200,
  maxWidth = 600 
}: Props) {
  const [width, setWidth] = useState(defaultWidth);
  const [isResizing, setIsResizing] = useState(false);

  const startResizing = useCallback((e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback((e: MouseEvent) => {
    if (isResizing) {
      const newWidth = e.clientX;
      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setWidth(newWidth);
      }
    }
  }, [isResizing, minWidth, maxWidth]);

  React.useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', resize);
      window.addEventListener('mouseup', stopResizing);
    }

    return () => {
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResizing);
    };
  }, [isResizing, resize, stopResizing]);

  return (
    <div 
      className="relative h-screen"
      style={{ width: `${width}px` }}
    >
      <div className="h-full overflow-y-auto bg-gray-800/50 backdrop-blur-sm border-r border-gray-700">
        <div className="p-4 mt-12">
          <h2 className="text-xl font-medium text-gray-200 mb-4">Summary History</h2>
          <div className="space-y-4">
            {summaryHistory.map((sum, index) => (
              <div 
                key={index} 
                className="p-4 rounded-lg bg-gray-800 border border-gray-700 hover:bg-gray-700/50 transition-colors cursor-pointer"
                onClick={() => onSelectSummary(sum)}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <span className="text-sm font-medium text-gray-300">{sum.channelName}</span>
                    <span className="text-xs text-gray-400 block">
                      {new Date(sum.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 ml-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteSummary(sum);
                      }}
                      className="p-1.5 hover:bg-red-500/20 text-red-400 hover:text-red-300 rounded-lg transition-colors"
                      title="Delete summary"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
                <p 
                    className="text-sm text-gray-300 line-clamp-3"
                >
                  {sum.text}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div
        className="absolute top-0 right-0 w-1 h-full cursor-col-resize bg-gray-700 hover:bg-blue-500 transition-colors"
        onMouseDown={startResizing}
      />
    </div>
  );
} 