import { NextResponse } from "next/server";
import { fal } from "@fal-ai/client";

export const runtime = "nodejs";

// Ensure credentials are configured from env
if (process.env.FAL_KEY) {
  fal.config({ credentials: process.env.FAL_KEY });
}

export async function POST(req: Request) {
  try {
    const contentType = req.headers.get("content-type") || "";
    if (!contentType.includes("multipart/form-data")) {
      return NextResponse.json({ error: "Expected multipart/form-data" }, { status: 400 });
    }

    const form = await req.formData();
    const image = form.get("image");
    const userPrompt = form.get("prompt");
    const aspectRatio = (form.get("aspect_ratio") as string) || "16:9"; // Prefer predictable framing
    const duration = (form.get("duration") as string) || "5s";

    if (!image || !(image instanceof File)) {
      return NextResponse.json({ error: "Field 'image' is required and must be a file." }, { status: 400 });
    }

    // Default prompt tailored for a room tour animation
    const defaultPrompt = "Create a smooth room tour from this single photo: slow parallax, gentle dolly and pan revealing the space, realistic depth and light, natural motion, steady camera, detailed textures, cinematic look.";
    const prompt = (typeof userPrompt === "string" && userPrompt.trim().length > 0) ? userPrompt : defaultPrompt;

    // Upload the image to FAL storage to get a stable URL
    const imageUrl = await fal.storage.upload(image);

    const result = await fal.subscribe("fal-ai/veo2/image-to-video", {
      input: {
        prompt,
        image_url: imageUrl,
        aspect_ratio: aspectRatio,
        duration,
      },
      logs: true,
      onQueueUpdate: (update) => {
        if (update.status === "IN_PROGRESS") {
          update.logs?.map((log) => log.message).forEach((m) => console.log("[veo2]", m));
        }
      },
    });

    return NextResponse.json({
      requestId: result.requestId,
      data: result.data,
    });
  } catch (error: any) {
    console.error("/api/room-tour error:", error);
    const message = error?.message || "Unexpected error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}


