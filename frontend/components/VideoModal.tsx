type VideoModalProps = {
  src: string;
  type: string;
  onClose: () => void;
}

export default function VideoModal({ src, type, onClose }: VideoModalProps) {
  return (
    <div 
      className="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div className="relative max-w-[90vw] max-h-[90vh]">
        <video
          controls
          autoPlay
          className="max-w-full max-h-[90vh] rounded-lg ring-1 ring-white/10"
          onClick={(e) => e.stopPropagation()}
        >
          <source src={src} type={type} />
          Your browser does not support the video tag.
        </video>
        <button
          onClick={onClose}
          className="absolute -top-2 -right-2 text-gray-300 bg-gray-800/90 rounded-full w-8 h-8 flex items-center justify-center hover:bg-gray-700/90 transition-colors ring-1 ring-white/10"
        >
          ×
        </button>
      </div>
    </div>
  )
} 