"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, BatchInfo, DashboardStats } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Download,
  Trash2,
  Filter,
  ChevronLeft,
  ChevronRight,
  Plus,
  Loader2,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Users } from "lucide-react";

export default function DashboardPage() {
  // State
  const [batches, setBatches] = useState<BatchInfo[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalBatches, setTotalBatches] = useState(0);
  const [limit] = useState(10); // Items per page

  // Fetch Data
  const loadData = async () => {
    setIsLoading(true);
    try {
      // Run both fetch requests in parallel
      const [batchesData, statsData] = await Promise.all([
        api.getBatches(page, limit),
        api.getStats(),
      ]);

      setBatches(batchesData.batches);
      setTotalBatches(batchesData.total);
      setStats(statsData);
    } catch (error) {
      console.error("Failed to load dashboard data", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [page]); // Reload when page changes

  // Handlers
  const handleDelete = async (batchId: string) => {
    if (!confirm("Are you sure you want to delete this batch?")) return;

    try {
      await api.deleteBatch(batchId);
      loadData(); // Refresh list
    } catch (error) {
      alert("Failed to delete batch");
    }
  };

  const handleDownloadZip = async (batchId: string) => {
    try {
      const blob = await api.downloadBatchZip(batchId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `batch_${batchId}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Download failed", error);
      alert("Could not download batch");
    }
  };

  // Helper to calculate total pages
  const totalPages = Math.ceil(totalBatches / limit);

  return (
    <div className="space-y-8">
      {/* --- Top Section: Stats Cards --- */}

      {/* --- Bottom Section: Batches Table --- */}
      <div className="bg-white rounded-lg shadow-sm border p-6 min-h-[400px]">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold">Tickets</h2>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>
              {batches.length} of {totalBatches}
            </span>
            <Button variant="ghost" size="icon">
              <Filter className="h-5 w-5" />
            </Button>
            {/* New Upload Button */}
            {/* <Link href="/upload/new">
              <Button className="gap-2">
                <Plus className="h-4 w-4" /> New Upload
              </Button>
            </Link> */}
            <div className="flex items-center gap-2">
              {/* NEW: Agencies Button */}
              <Link href="/agencies">
                <Button variant="outline" className="gap-2">
                  <Users className="h-4 w-4" /> Agencies
                </Button>
              </Link>

              <Link href="/upload/new">
                <Button className="gap-2">
                  <Plus className="h-4 w-4" /> New Upload
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="h-64 flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[150px]">Batch ID</TableHead>
                  <TableHead>File Name</TableHead>
                  <TableHead className="text-center">Total</TableHead>
                  <TableHead className="text-center">Generated</TableHead>
                  <TableHead className="text-center">Failed</TableHead>
                  <TableHead className="text-center">Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {batches.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={7}
                      className="h-24 text-center text-gray-500"
                    >
                      No batches found. Upload a file to get started.
                    </TableCell>
                  </TableRow>
                ) : (
                  batches.map((batch) => (
                    <TableRow key={batch.batch_id} className="hover:bg-gray-50">
                      <TableCell className="font-mono text-xs text-gray-500">
                        {batch.batch_id.substring(0, 8)}
                      </TableCell>

                      {/* File Name Link */}
                      <TableCell className="max-w-[250px]">
                        <Link
                          href={`/upload/${batch.batch_id}`}
                          className="flex items-center gap-2 hover:text-blue-600 group"
                        >
                          <FileText className="h-4 w-4 text-gray-400 group-hover:text-blue-500" />
                          <span className="truncate font-medium">Open</span>
                        </Link>
                      </TableCell>

                      <TableCell className="text-center">
                        <Badge
                          variant="secondary"
                          className="rounded-full px-3 font-mono"
                        >
                          {batch.total_passengers}
                        </Badge>
                      </TableCell>

                      <TableCell className="text-center">
                        <Badge
                          variant="outline"
                          className="rounded-full px-3 font-mono bg-green-50 text-green-700 border-green-200"
                        >
                          {batch.generated}
                        </Badge>
                      </TableCell>

                      <TableCell className="text-center">
                        <Badge
                          variant="outline"
                          className="rounded-full px-3 font-mono bg-red-50 text-red-700 border-red-200"
                        >
                          {batch.failed}
                        </Badge>
                      </TableCell>

                      <TableCell className="text-center">
                        <span
                          className={cn(
                            "text-xs uppercase font-bold tracking-wider",
                            batch.status === "completed"
                              ? "text-green-600"
                              : batch.status === "processing"
                              ? "text-blue-600"
                              : "text-red-600"
                          )}
                        >
                          {batch.status}
                        </span>
                      </TableCell>

                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => handleDownloadZip(batch.batch_id)}
                            disabled={batch.status !== "completed"}
                            title="Download ZIP"
                          >
                            <Download className="h-4 w-4 text-gray-500" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 hover:bg-red-50"
                            onClick={() => handleDelete(batch.batch_id)}
                            title="Delete Batch"
                          >
                            <Trash2 className="h-4 w-4 text-red-400" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>

            {/* Pagination */}
            {totalBatches > limit && (
              <div className="flex justify-end items-center gap-4 mt-6 text-sm text-gray-600">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-5 w-5" />
                </Button>

                <span className="font-medium text-black">
                  Page {page} of {totalPages}
                </span>

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  <ChevronRight className="h-5 w-5" />
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
