type ImageModalProps = {
  src: string;
  alt: string;
  onClose: () => void;
}

export default function ImageModal({ src, alt, onClose }: ImageModalProps) {
  return (
    <div 
      className="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div className="relative max-w-[90vw] max-h-[90vh]">
        <img
          src={src}
          alt={alt}
          className="max-w-full max-h-[90vh] object-contain rounded-lg ring-1 ring-white/10"
          onClick={(e) => e.stopPropagation()}
        />
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