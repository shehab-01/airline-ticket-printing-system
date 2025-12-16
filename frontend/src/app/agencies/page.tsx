"use client";

import { useEffect, useState, useRef } from "react";
import { agencyApi, Agency, AgencyFormData } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Loader2, Plus, Trash2, Building2, Upload } from "lucide-react";
import { toast } from "sonner";

export default function AgenciesPage() {
  // State
  const [agencies, setAgencies] = useState<Agency[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  // Form State
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState({
    agency_name: "",
    agency_owner: "",
    agency_address: "",
    email: "",
    telephone: "",
  });

  // --- Fetch Agencies using API Client ---
  const loadAgencies = async () => {
    setIsLoading(true);
    try {
      const data = await agencyApi.listAgencies(1, 100);

      setAgencies(data.agencies || []);
    } catch (error) {
      console.error(error);
      toast.error("Failed to load agencies");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAgencies();
  }, []);

  // ---  Create Agency Handler ---
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);

    try {
      const payload: AgencyFormData = {
        agency_name: formData.agency_name,
        agency_owner: formData.agency_owner,
        agency_address: formData.agency_address,
        email: formData.email,
        telephone: formData.telephone,
        logo: fileInputRef.current?.files?.[0] || null,
      };

      await agencyApi.createAgency(payload);

      toast.success("Agency created successfully");

      // Reset Form
      setFormData({
        agency_name: "",
        agency_owner: "",
        agency_address: "",
        email: "",
        telephone: "",
      });
      if (fileInputRef.current) fileInputRef.current.value = "";

      // Reload list
      loadAgencies();
    } catch (error: any) {
      console.error(error);
      const msg = error.response?.data?.detail || "Failed to create agency";
      toast.error(msg);
    } finally {
      setIsCreating(false);
    }
  };

  // ---  Delete Handler ---
  const handleDelete = async (id: string) => {
    if (!confirm("Delete this agency?")) return;

    try {
      await agencyApi.deleteAgency(id);
      toast.success("Agency deleted");
      loadAgencies();
    } catch (error) {
      toast.error("Failed to delete agency");
    }
  };

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Agency Management</h1>
      </div>

      {/* --- TOP SECTION: CREATE FORM --- */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Plus className="h-5 w-5 text-blue-600" /> Create New Agency
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreate} className="grid gap-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Agency Name *</Label>
                <Input
                  id="name"
                  required
                  placeholder="e.g. APA Travels"
                  value={formData.agency_name}
                  onChange={(e) =>
                    setFormData({ ...formData, agency_name: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="owner">Owner Name *</Label>
                <Input
                  id="owner"
                  required
                  placeholder="e.g. MD Shamim"
                  value={formData.agency_owner}
                  onChange={(e) =>
                    setFormData({ ...formData, agency_owner: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="contact@agency.com"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Telephone</Label>
                <Input
                  id="phone"
                  placeholder="010-1234-5678"
                  value={formData.telephone}
                  onChange={(e) =>
                    setFormData({ ...formData, telephone: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="address">Address</Label>
                <Input
                  id="address"
                  placeholder="Full  address"
                  value={formData.agency_address}
                  onChange={(e) =>
                    setFormData({ ...formData, agency_address: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="logo">Logo (Optional)</Label>
                <div className="flex items-center gap-2">
                  <Input
                    id="logo"
                    type="file"
                    accept="image/*"
                    ref={fileInputRef}
                    className="cursor-pointer"
                  />
                </div>
                <p className="text-xs text-gray-500">Supports PNG, JPG, SVG.</p>
              </div>
            </div>

            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={isCreating}
                className="min-w-[150px]"
              >
                {isCreating ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="mr-2 h-4 w-4" />
                )}
                {isCreating ? "Creating..." : "Create Agency"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* --- BOTTOM SECTION: LIST VIEW --- */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Building2 className="h-5 w-5 text-gray-600" /> Existing Agencies
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="h-40 flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-gray-300" />
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-20">Logo</TableHead>
                    <TableHead>Agency Name</TableHead>
                    <TableHead>Owner</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Address</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {agencies.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={6}
                        className="h-24 text-center text-gray-500"
                      >
                        No agencies found. Create one above.
                      </TableCell>
                    </TableRow>
                  ) : (
                    agencies.map((agency) => (
                      <TableRow key={agency.id}>
                        <TableCell>
                          <div className="h-10 w-10 relative overflow-hidden rounded-full border bg-gray-50 flex items-center justify-center">
                            <img
                              src={agencyApi.getLogoUrl(agency.id)}
                              alt={agency.agency_name}
                              className="h-full w-full object-cover"
                              onError={(e) => {
                                e.currentTarget.style.display = "none";
                                e.currentTarget.nextElementSibling?.classList.remove(
                                  "hidden"
                                );
                              }}
                            />
                            <Building2 className="h-5 w-5 text-gray-300 hidden absolute" />
                          </div>
                        </TableCell>
                        <TableCell className="font-medium">
                          {agency.agency_name}
                        </TableCell>
                        <TableCell>{agency.agency_owner}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div className="text-gray-900">
                              {agency.email || "-"}
                            </div>
                            <div className="text-gray-500 text-xs">
                              {agency.telephone}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-gray-500 truncate max-w-[200px]">
                          {agency.agency_address || "-"}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-500 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDelete(agency.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
