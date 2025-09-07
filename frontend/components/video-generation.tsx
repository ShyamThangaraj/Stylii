"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"

interface VideoGenerationProps {
  imageUrl: string
}

interface VideoProgress {
  status: string
  message: string
  progress?: number
  result?: {
    output_path: string
    duration: number
  }
}

export function VideoGeneration({ imageUrl }: VideoGenerationProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState<VideoProgress | null>(null)
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerateVideo = async () => {
    setIsGenerating(true)
    setError(null)
    setProgress(null)
    setVideoUrl(null)

    try {
      // Convert image URL to File object
      const response = await fetch(imageUrl)
      const blob = await response.blob()
      const file = new File([blob], 'room-image.jpg', { type: 'image/jpeg' })

      // Create FormData
      const formData = new FormData()
      formData.append('image', file)

      // Call the video generation server
      const videoResponse = await fetch('http://localhost:5001/generate', {
        method: 'POST',
        body: formData,
      })

      if (!videoResponse.ok) {
        throw new Error(`Server error: ${videoResponse.status}`)
      }

      const result = await videoResponse.json()

      if (result.status === 'success') {
        setProgress({
          status: 'completed',
          message: 'Video generation completed!',
          progress: 100,
          result: result.result
        })
        // In a real implementation, you'd need to serve the video file
        // For now, we'll just show success
      } else {
        throw new Error(result.message || 'Video generation failed')
      }
    } catch (err) {
      console.error('Video generation error:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate video')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleGenerateVideoWithStream = async () => {
    setIsGenerating(true)
    setError(null)
    setProgress(null)
    setVideoUrl(null)

    try {
      // Convert image URL to File object
      const response = await fetch(imageUrl)
      const blob = await response.blob()
      const file = new File([blob], 'room-image.jpg', { type: 'image/jpeg' })

      // Create FormData
      const formData = new FormData()
      formData.append('image', file)

      // Call the streaming video generation server
      const videoResponse = await fetch('http://localhost:5001/generate/stream', {
        method: 'POST',
        body: formData,
      })

      if (!videoResponse.ok) {
        throw new Error(`Server error: ${videoResponse.status}`)
      }

      const reader = videoResponse.body?.getReader()
      if (!reader) {
        throw new Error('Unable to read response stream')
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = new TextDecoder().decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              setProgress(data)

              if (data.status === 'completed' || data.status === 'error') {
                setIsGenerating(false)
                if (data.status === 'error') {
                  setError(data.message)
                }
                return
              }
            } catch (e) {
              // Ignore JSON parse errors for malformed chunks
            }
          }
        }
      }
    } catch (err) {
      console.error('Video generation error:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate video')
      setIsGenerating(false)
    }
  }

  return (
    <div className="blueprint-card p-6">
      <h3 className="text-lg font-bold blueprint-text mb-4" style={{color: 'var(--blueprint-charcoal)'}}>
        Generate Room Tour Video
      </h3>

      <p className="blueprint-text text-sm mb-6" style={{color: 'var(--blueprint-blue)'}}>
        Create a 360° room tour video with AI-generated narration showcasing your design.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {error}
        </div>
      )}

      {progress && (
        <div className="mb-4 space-y-2">
          <div className="flex justify-between items-center">
            <span className="blueprint-label text-xs">STATUS</span>
            <span className="blueprint-text text-sm" style={{color: 'var(--blueprint-amber)'}}>
              {progress.progress}%
            </span>
          </div>
          <Progress value={progress.progress || 0} className="w-full" />
          <p className="blueprint-text text-sm" style={{color: 'var(--blueprint-blue)'}}>
            {progress.message}
          </p>

          {progress.status === 'completed' && progress.result && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
              <p className="text-green-700 text-sm font-medium">
                ✅ Video generated successfully! Duration: {progress.result.duration.toFixed(1)}s
              </p>
              <p className="text-green-600 text-xs mt-1">
                Output: {progress.result.output_path}
              </p>
            </div>
          )}
        </div>
      )}

      <div className="flex gap-3">
        <Button
          onClick={handleGenerateVideo}
          disabled={isGenerating}
          className="blueprint-button blueprint-button-primary flex-1"
        >
          {isGenerating ? 'Generating...' : 'Generate Video'}
        </Button>

        <Button
          onClick={handleGenerateVideoWithStream}
          disabled={isGenerating}
          variant="outline"
          className="blueprint-button flex-1"
        >
          {isGenerating ? 'Streaming...' : 'Generate with Progress'}
        </Button>
      </div>
    </div>
  )
}
