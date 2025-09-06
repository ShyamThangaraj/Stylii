"use client"

import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { X, Upload } from "lucide-react"
import { Button } from "@/components/ui/button"
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
      {images.length < 4 && (
        <div className="space-y-3">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-2xl p-6 md:p-8 text-center cursor-pointer transition-colors ${
              isDragActive ? "border-orange-400 bg-orange-50" : "border-gray-300 hover:border-orange-400"
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-8 h-8 md:w-12 md:h-12 mx-auto mb-3 md:mb-4 text-gray-400" />
            <p className="text-base md:text-lg font-medium mb-2">
              {isDragActive ? "Drop images here" : "Drag & drop room photos"}
            </p>
            <p className="text-sm md:text-base text-gray-500">or click to browse • {4 - images.length} more needed</p>
          </div>
        </div>
      )}

      {images.length > 0 && (
        <div className="grid grid-cols-2 gap-3 md:gap-4">
          {images.map((image, index) => (
            <div key={index} className="relative group">
              <img
                src={URL.createObjectURL(image) || "/placeholder.svg"}
                alt={`Room photo ${index + 1}`}
                className="w-full h-24 md:h-32 object-cover rounded-lg"
              />
              <Button
                size="sm"
                variant="destructive"
                className="absolute top-1 right-1 md:top-2 md:right-2 w-5 h-5 md:w-6 md:h-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={() => removeImage(index)}
              >
                <X className="w-3 h-3 md:w-4 md:h-4" />
              </Button>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs md:text-sm text-gray-500">
        {images.length}/4 photos uploaded
        {images.length >= 3 && <span className="text-green-600 ml-2">✓ Ready to generate</span>}
      </p>
    </div>
  )
}
