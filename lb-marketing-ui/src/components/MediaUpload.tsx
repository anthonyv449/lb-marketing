import React from "react";
import { Input } from "./ui/input";
import { Label } from "./ui/Label";

interface MediaUploadProps {
  onFileChange: (file: File | null) => void;
  onError: (error: string | null) => void;
  mediaFile: File | null;
}

export default function MediaUpload({
  onFileChange,
  onError,
  mediaFile,
}: MediaUploadProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
      ];
      if (!validTypes.includes(file.type)) {
        onError(
          "Invalid file type. Please upload JPEG, PNG, GIF, or WEBP only."
        );
        e.target.value = "";
        return;
      }
      onFileChange(file);
      onError(null);
    } else {
      onFileChange(null);
    }
  };

  return (
    <div className="flex flex-col gap-2 md:col-span-2">
      <Label htmlFor="mediaFile">
        Media Upload, accepting images or gifs only
      </Label>
      <Input
        id="mediaFile"
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp"
        onChange={handleFileChange}
      />
      {mediaFile && (
        <p className="text-sm text-muted-foreground">
          Selected: {mediaFile.name} (
          {(mediaFile.size / 1024 / 1024).toFixed(2)} MB)
        </p>
      )}
    </div>
  );
}

