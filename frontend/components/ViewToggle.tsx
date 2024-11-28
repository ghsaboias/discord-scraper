
interface Props {
  view: 'grid' | 'list';
  onViewChange: (view: 'grid' | 'list') => void;
}

export default function ViewToggle({ view, onViewChange }: Props) {
  return (
    <div className="flex items-center space-x-2 mb-4">
      <button
        onClick={() => onViewChange('list')}
        className={`p-2 rounded-lg transition-colors ${
          view === 'list' 
            ? 'bg-blue-500 text-white' 
            : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
        }`}
        title="List view"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <button
        onClick={() => onViewChange('grid')}
        className={`p-2 rounded-lg transition-colors ${
          view === 'grid' 
            ? 'bg-blue-500 text-white' 
            : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
        }`}
        title="Grid view"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
      </button>
    </div>
  );
} 