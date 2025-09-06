"use client"

import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { useStyliiStore } from "@/lib/store"

export function UploadDropzone() {
  const { images, setImages } = useStyliiStore()
  const [isDragActive, setIsDragActive] = useState(false)

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const newImages = [...images, ...acceptedFiles].slice(0, 4)
      setImages(newImages)
    },
    [images, setImages],
  )

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".webp"],
    },
    maxFiles: 4 - images.length,
    disabled: images.length >= 4,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
  })

  const removeImage = (index: number) => {
    const newImages = images.filter((_, i) => i !== index)
    setImages(newImages)
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="blueprint-label">IMAGE DOCUMENTATION</div>
        {images.length < 4 && (
          <div
            {...getRootProps()}
            className={`blueprint-upload p-8 text-center cursor-pointer ${
              isDragActive ? "active" : ""
            }`}
          >
            <input {...getInputProps()} />
            <div className="blueprint-label mb-4">UPLOAD</div>
            <p className="blueprint-text text-base font-medium mb-2" style={{color: 'var(--blueprint-charcoal)'}}>
              {isDragActive ? "DROP FILES HERE" : "UPLOAD ROOM IMAGES"}
            </p>
            <p className="blueprint-text text-sm" style={{color: 'var(--blueprint-blue)'}}>
              Drag and drop files or click to browse • {images.length === 0 ? '1 image required' : `${4 - images.length} more optional`}
            </p>
          </div>
        )}
      </div>

      {images.length > 0 && (
        <div className="space-y-3">
          <div className="blueprint-label">UPLOADED FILES</div>
          <div className="grid grid-cols-2 gap-3">
            {images.map((image, index) => (
              <div key={index} className="relative group blueprint-card">
                <img
                  src={URL.createObjectURL(image) || "/placeholder.svg"}
                  alt={`Room image ${index + 1}`}
                  className="w-full h-32 object-cover"
                />
                <div className="absolute top-2 left-2 blueprint-label text-xs bg-white px-1">
                  {String(index + 1).padStart(2, '0')}
                </div>
                <button
                  className="absolute top-2 right-2 w-6 h-6 blueprint-button-primary text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => removeImage(index)}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between blueprint-label">
        <span>FILES: {images.length}/4</span>
        {images.length >= 1 && <span style={{color: 'var(--blueprint-amber)'}}>READY FOR ANALYSIS</span>}
      </div>
    </div>
  )
}
