"use client";

import { useEffect, useState, useRef, use } from "react"; // 1. Import 'use'
import { useRouter } from "next/navigation";
import { api, BatchStatusResponse } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  UploadCloud,
  Download,
  Loader2,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
} from "lucide-react";
import { cn } from "@/lib/utils";

// 2. Update props type to Promise
export default function BatchDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  // 3. Unwrap the params using React.use()
  const { id } = use(params);

  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 4. Use 'id' directly instead of 'params.id'
  const [isNewUpload, setIsNewUpload] = useState(id === "new");
  const [batchId, setBatchId] = useState<string>(id === "new" ? "" : id);
  const [isUploading, setIsUploading] = useState(false);
  const [batchStatus, setBatchStatus] = useState<BatchStatusResponse | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Poll for status if we have a batch ID and it's not complete
  useEffect(() => {
    if (!batchId || isNewUpload) return;

    const fetchStatus = async () => {
      try {
        const data = await api.getBatchStatus(batchId);
        setBatchStatus(data);

        // Stop polling if complete or failed
        if (data.status === "completed" || data.status === "failed") {
          return;
        }
      } catch (err) {
        console.error("Polling error", err);
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll every 2 seconds
    const interval = setInterval(() => {
      if (
        batchStatus?.status !== "completed" &&
        batchStatus?.status !== "failed"
      ) {
        fetchStatus();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [batchId, isNewUpload, batchStatus?.status]);

  // --- File Upload Handlers ---

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await processUpload(e.target.files[0]);
    }
  };

  const processUpload = async (file: File) => {
    setError(null);

    // 1. Strict Frontend Validation
    const validExtensions = [".xlsx", ".xls"];
    const fileExtension = file.name
      .toLowerCase()
      .slice(file.name.lastIndexOf("."));

    if (!validExtensions.includes(fileExtension)) {
      setError(
        "Invalid file type. Please upload only Excel files (.xlsx or .xls)"
      );
      return;
    }

    try {
      setIsUploading(true);

      // 2. Call API
      const response = await api.uploadFile(file);

      // 3. Handle Success
      setBatchId(response.batch_id);
      setIsNewUpload(false);

      // Update URL without refreshing
      window.history.replaceState(null, "", `/upload/${response.batch_id}`);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Upload failed. Please try again."
      );
    } finally {
      setIsUploading(false);
    }
  };

  // Drag and Drop Visuals
  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const onDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };
  const onDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processUpload(e.dataTransfer.files[0]);
    }
  };

  // --- Render Helpers ---

  const getStatusBadge = (status: string, errorMsg?: string) => {
    if (status === "generated") {
      return (
        <Badge
          variant="outline"
          className="rounded-full border-green-200 bg-green-50 text-green-700 font-normal gap-1"
        >
          <CheckCircle2 className="h-3 w-3" /> Done
        </Badge>
      );
    }
    if (status === "failed") {
      return (
        <Badge
          variant="outline"
          className="rounded-full border-red-200 bg-red-50 text-red-700 font-normal gap-1"
          title={errorMsg}
        >
          <AlertCircle className="h-3 w-3" /> Failed
        </Badge>
      );
    }
    return (
      <Badge
        variant="outline"
        className="rounded-full border-gray-300 text-gray-600 font-normal gap-1"
      >
        <Loader2 className="h-3 w-3 animate-spin" /> Pending
      </Badge>
    );
  };

  const handleDownloadSingle = async (filename?: string) => {
    if (!filename || !batchId) return;
    try {
      const blob = await api.downloadSinglePdf(batchId, filename);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) {
      console.error("Download failed", e);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-8 min-h-[80vh]">
      {/* --- Error Message --- */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          {error}
        </div>
      )}

      {/* --- Upload Area (Only visible for new uploads) --- */}
      {isNewUpload && (
        <div
          className={cn(
            "border-2 border-dashed rounded-xl h-64 flex flex-col items-center justify-center transition-all cursor-pointer",
            isDragging
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 bg-gray-50/50 hover:bg-gray-100",
            isUploading && "opacity-50 pointer-events-none"
          )}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          {isUploading ? (
            <div className="flex flex-col items-center">
              <Loader2 className="h-12 w-12 text-blue-500 animate-spin mb-4" />
              <p className="text-lg font-medium text-gray-700">
                Uploading & Processing...
              </p>
            </div>
          ) : (
            <>
              <FileSpreadsheet
                className={cn(
                  "h-16 w-16 mb-4",
                  isDragging ? "text-blue-500" : "text-gray-400"
                )}
              />
              <h3 className="text-xl font-semibold text-gray-700">
                Upload Excel File
              </h3>
              <p className="text-sm text-gray-500 mt-2">
                Drag & drop or click to upload (.xlsx, .xls)
              </p>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".xlsx, .xls, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                onChange={handleFileSelect}
              />
            </>
          )}
        </div>
      )}

      {/* --- Detail View (Visible once batch exists) --- */}
      {!isNewUpload && batchStatus && (
        <>
          {/* Stats Header */}
          <div className="py-8 flex flex-col items-center justify-center gap-2 border-b border-gray-100">
            <h2 className="text-2xl font-medium text-gray-800">
              Total found:{" "}
              <span className="font-mono">{batchStatus.total_passengers}</span>
            </h2>

            <div className="w-full flex justify-end text-sm text-gray-500 items-center gap-2">
              {batchStatus.status === "processing" ? (
                <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
              ) : batchStatus.status === "completed" ? (
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              ) : null}

              <span>
                Generated{" "}
                <span className="font-semibold text-gray-700">
                  {batchStatus.generated}
                </span>{" "}
                of {batchStatus.total_passengers}
              </span>

              {/* Batch Download Button */}
              {batchStatus.status === "completed" && (
                <Button
                  variant="outline"
                  size="sm"
                  className="ml-4 gap-2"
                  onClick={() => api.downloadBatchZip(batchId)}
                >
                  <Download className="h-4 w-4" /> Download All (ZIP)
                </Button>
              )}
            </div>
          </div>

          {/* Passengers Table */}
          <div className="mt-6">
            <Table>
              <TableHeader className="bg-transparent border-b-0">
                <TableRow className="hover:bg-transparent border-b-0 text-gray-500 text-xs uppercase tracking-wider">
                  <TableHead>No.</TableHead>
                  <TableHead>Passenger Name</TableHead>
                  <TableHead>PNR</TableHead>
                  <TableHead className="text-center">Type</TableHead>
                  <TableHead className="text-center">State</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {batchStatus.passengers.map((pax, index) => (
                  <TableRow
                    key={index}
                    className={`border-b-0 ${
                      index % 2 === 0 ? "" : "bg-gray-50/50"
                    }`}
                  >
                    <TableCell className="font-mono text-xs text-gray-500 py-6">
                      {pax.no || index + 1}
                    </TableCell>
                    <TableCell className="font-medium text-sm py-6">
                      {pax.pax_name}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-gray-500 py-6">
                      {pax.pnr}
                    </TableCell>
                    <TableCell className="text-center text-sm py-6">
                      {pax.ticket_type}
                    </TableCell>
                    <TableCell className="text-center py-6">
                      {getStatusBadge(pax.status, pax.error)}
                    </TableCell>
                    <TableCell className="text-right py-6">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 hover:bg-gray-200"
                        disabled={pax.status !== "generated"}
                        onClick={() => handleDownloadSingle(pax.pdf_filename)}
                      >
                        <Download
                          className={cn(
                            "h-5 w-5",
                            pax.status === "generated"
                              ? "text-gray-600"
                              : "text-gray-300"
                          )}
                        />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </>
      )}
    </div>
  );
}
