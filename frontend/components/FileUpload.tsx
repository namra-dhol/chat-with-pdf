/**
 * components/FileUpload.tsx
 * -------------------------
 * Drag-and-drop PDF upload component with visual feedback.
 */

"use client";

import React, { useCallback, useRef, useState } from "react";
import { uploadPdf, UploadResponse } from "@/services/api";

interface FileUploadProps {
    onSuccess: (data: UploadResponse) => void;
}

export function FileUpload({ onSuccess }: FileUploadProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const validateFile = (file: File): string | null => {
        if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
            return "Only PDF files are accepted.";
        }
        if (file.size > 50 * 1024 * 1024) {
            return "File size must be under 50 MB.";
        }
        return null;
    };

    const handleFile = useCallback(async (file: File) => {
        const validationError = validateFile(file);
        if (validationError) {
            setError(validationError);
            return;
        }

        setError(null);
        setSelectedFile(file);
        setIsUploading(true);

        try {
            const result = await uploadPdf(file);
            onSuccess(result);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Upload failed. Please try again.");
            setSelectedFile(null);
        } finally {
            setIsUploading(false);
        }
    }, [onSuccess]);

    const handleDrop = useCallback(
        (e: React.DragEvent<HTMLDivElement>) => {
            e.preventDefault();
            setIsDragging(false);
            const file = e.dataTransfer.files[0];
            if (file) handleFile(file);
        },
        [handleFile]
    );

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => setIsDragging(false);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) handleFile(file);
    };

    return (
        <div className="w-full max-w-xl mx-auto">
            {/* Drop Zone */}
            <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => !isUploading && inputRef.current?.click()}
                className={`
          relative rounded-2xl border-2 border-dashed p-12 text-center cursor-pointer
          transition-all duration-300 ease-in-out
          ${isDragging
                        ? "border-violet-400 bg-violet-500/20 scale-105"
                        : "border-white/20 bg-white/5 hover:border-violet-500/50 hover:bg-violet-500/5"
                    }
          ${isUploading ? "cursor-not-allowed opacity-60" : ""}
        `}
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept=".pdf,application/pdf"
                    className="hidden"
                    onChange={handleInputChange}
                    disabled={isUploading}
                />

                {/* Icon */}
                <div className="flex justify-center mb-4">
                    {isUploading ? (
                        <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
                    ) : (
                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-colors ${isDragging ? "bg-violet-500/30" : "bg-white/10"
                            }`}>
                            <svg className="w-8 h-8 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                                />
                            </svg>
                        </div>
                    )}
                </div>

                {/* Text */}
                {isUploading ? (
                    <div>
                        <p className="text-violet-300 font-semibold text-lg">Processing PDF...</p>
                        <p className="text-gray-500 text-sm mt-1">
                            {selectedFile?.name} — Generating embeddings
                        </p>
                    </div>
                ) : (
                    <div>
                        <p className="text-white font-semibold text-lg mb-1">
                            {isDragging ? "Drop your PDF here!" : "Drag & Drop your PDF"}
                        </p>
                        <p className="text-gray-400 text-sm">or click to browse</p>
                        <p className="text-gray-600 text-xs mt-3">PDF files only · Max 50 MB</p>
                    </div>
                )}
            </div>

            {/* Error */}
            {error && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl">
                    <p className="text-red-400 text-sm text-center">{error}</p>
                </div>
            )}
        </div>
    );
}
