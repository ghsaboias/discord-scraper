import { Summary } from '@/types/discord';
import React, { useCallback, useState } from 'react';

interface Props {
  summaryHistory: Summary[];
  onSelectSummary: (summary: Summary) => void;
  defaultWidth?: number;
  minWidth?: number;
  maxWidth?: number;
}

export default function ResizableSidebar({ 
  summaryHistory, 
  onSelectSummary,
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
                className="p-4 rounded-lg bg-gray-800 border border-gray-700 cursor-pointer hover:bg-gray-700/50 transition-colors"
                onClick={() => onSelectSummary(sum)}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm font-medium text-gray-300">{sum.channelName}</span>
                  <span className="text-xs text-gray-400">
                    {new Date(sum.timestamp).toLocaleString()}
                  </span>
                </div>
                <p className="text-sm text-gray-300 line-clamp-3">{sum.text}</p>
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