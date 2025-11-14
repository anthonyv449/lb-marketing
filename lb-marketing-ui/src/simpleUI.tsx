import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardContent } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Textarea } from "./components/ui/textarea";
import { Button } from "./components/ui/button";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "./components/ui/select";
import { Switch } from "./components/ui/Switch";
import { Label } from "./components/ui/Label";
import { ScrollArea } from "./components/ui/ScrollArea";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/Tabs";
import {
  Instagram,
  Twitter,
  Facebook,
  Linkedin,
  Youtube,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { api } from "./lib/api";

export default function SimpleMarketingDashboard() {
  interface Post {
    platform: string;
    tone: string;
    mediaUrl: string;
    content: string;
    schedule: boolean;
  }
  const [platform, setPlatform] = useState<string>("twitter");
  const [tone, setTone] = useState<string>("professional");
  const [mediaUrl, setMediaUrl] = useState<string>("");
  const [content, setContent] = useState<string>("");
  const [schedule, setSchedule] = useState<boolean>(false);
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [xConnected, setXConnected] = useState<boolean>(false);
  const [xHandle, setXHandle] = useState<string | null>(null);
  const [checkingConnection, setCheckingConnection] = useState<boolean>(true);
  const [publishing, setPublishing] = useState<boolean>(false);

  const platformOptions = [
    { label: "Twitter", value: "twitter", icon: Twitter },
    { label: "Facebook", value: "facebook", icon: Facebook },
    { label: "Instagram", value: "instagram", icon: Instagram },
    { label: "LinkedIn", value: "linkedin", icon: Linkedin },
    { label: "YouTube", value: "youtube", icon: Youtube },
  ];

  const toneOptions = [
    { label: "Professional", value: "professional" },
    { label: "Casual", value: "casual" },
    { label: "Playful", value: "playful" },
    { label: "Inspirational", value: "inspirational" },
  ];

  // Map UI platform values to backend enum values
  const mapUiToBackendPlatform = (uiPlatform: string) => {
    if (uiPlatform === "twitter") return "x"; // backend uses `x` for Twitter
    return uiPlatform;
  };

  // Map backend platform values to UI equivalents for displaying icons
  const mapBackendToUiPlatform = (backendPlatform: string) => {
    if (backendPlatform === "x") return "twitter";
    return backendPlatform;
  };

  // Helper function to convert local datetime to UTC ISO string
  const convertLocalToUTC = (localDateTimeString: string): string => {
    // datetime-local input gives us a string like "2024-01-01T12:00" (no timezone)
    // JavaScript interprets this as local time when creating a Date object
    const localDate = new Date(localDateTimeString);
    // Convert to UTC ISO string for the API
    return localDate.toISOString();
  };

  // Helper function to get timezone name for display
  const getTimezoneName = (): string => {
    try {
      return Intl.DateTimeFormat().resolvedOptions().timeZone;
    } catch {
      return "local time";
    }
  };

  // Check X connection status on mount
  useEffect(() => {
    checkXConnection();
    
    // Handle OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const oauthParam = urlParams.get("oauth");
    if (oauthParam === "success") {
      // Clear the URL parameter
      window.history.replaceState({}, document.title, window.location.pathname);
      // Check connection status again
      setTimeout(() => checkXConnection(), 1000);
    }
  }, []);

  const checkXConnection = async () => {
    setCheckingConnection(true);
    try {
      const res = await api.checkXStatus(1);
      if (res.ok) {
        const data = await res.json();
        setXConnected(data.connected);
        setXHandle(data.handle);
      }
    } catch (err) {
      console.error("Failed to check X connection:", err);
      // Silently fail - OAuth is optional
    } finally {
      setCheckingConnection(false);
    }
  };

  const handleXSignIn = () => {
    // Redirect to backend OAuth endpoint
    api.authorizeX(1);
  };

  const handlePublishAll = async () => {
    setPublishing(true);
    setError(null);
    try {
      const res = await api.publishAllPosts();

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const published = await res.json();
      alert(`Successfully published ${published.length} post(s)!`);
      
      // Optionally refresh posts list
      // You might want to fetch posts from the API here
    } catch (err: any) {
      setError(err?.message || "Failed to publish posts");
    } finally {
      setPublishing(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!content.trim()) return;
    setLoading(true);

    // Build payload expected by backend ScheduledPostCreate
    // Note: backend requires `business_id` and `scheduled_at`.
    // Assumption: Use business_id = 1 by default (project doesn't expose business picker in this UI).
    // If scheduling is toggled, use the selected date (converted from local to UTC).
    // Otherwise, use current time (already in UTC via toISOString).
    const scheduledAt = schedule && selectedDate 
      ? convertLocalToUTC(selectedDate)
      : new Date().toISOString();
    
    const payload = {
      business_id: 1,
      platform: mapUiToBackendPlatform(platform),
      content: content.trim(),
      scheduled_at: scheduledAt,
      campaign_id: null,
      media_asset_id: null,
    };

    try {
      const res = await api.createPost(payload);

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const saved = await res.json();

      // saved should conform to ScheduledPostOut. Map to local Post shape for display.
      const displayPost: Post = {
        platform: mapBackendToUiPlatform(saved.platform),
        tone,
        mediaUrl: mediaUrl.trim(),
        content: saved.content ?? content.trim(),
        schedule: !!saved.scheduled_at,
      };

      setPosts([displayPost, ...posts]);

      // reset form
      setContent("");
      setMediaUrl("");
      setSchedule(false);
      setSelectedDate("");
    } catch (err: any) {
      setError(err?.message || "Failed to create post");
    } finally {
      setLoading(false);
    }
  };

  const getPlatformIcon = (platformKey: string) => {
    // Accept both UI and backend keys (backend may return 'x' for Twitter)
    const normalized = platformKey === "x" ? "twitter" : platformKey;
    const found = platformOptions.find((p) => p.value === normalized);
    return found ? <found.icon className="w-4 h-4 mr-2" /> : null;
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Marketing Dashboard</h1>
        <div className="flex items-center gap-4">
          {/* X Connection Status */}
          <div className="flex items-center gap-2">
            {checkingConnection ? (
              <span className="text-sm text-muted-foreground">Checking...</span>
            ) : xConnected ? (
              <div className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle2 className="w-4 h-4" />
                <span>X: @{xHandle}</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-red-500" />
                <Button
                  onClick={handleXSignIn}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <Twitter className="w-4 h-4" />
                  Connect X
                </Button>
              </div>
            )}
          </div>
          {/* Publish All Button */}
          <Button
            onClick={handlePublishAll}
            disabled={publishing}
            variant="default"
            size="sm"
          >
            {publishing ? "Publishing..." : "Publish All"}
          </Button>
        </div>
      </div>
      <Tabs defaultValue="compose">
        <TabsList className="bg-transparent mb-4">
          <TabsTrigger value="compose" className="px-4 py-2">Compose</TabsTrigger>
          <TabsTrigger value="posts" className="px-4 py-2">Posts</TabsTrigger>
        </TabsList>
        {/* Compose tab */}
        <TabsContent value="compose">
          <form
            onSubmit={handleSubmit}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {/* Platform selector */}
            <div className="flex flex-col gap-2">
              <Label htmlFor="platform">Platform</Label>
              <Select
                value={platform}
                onValueChange={(v) => setPlatform(v)}
              >
                <SelectTrigger id="platform" className="w-full">
                  <SelectValue placeholder="Select platform" />
                </SelectTrigger>
                <SelectContent>
                  {platformOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value} className="flex items-center">
                      <opt.icon className="w-4 h-4 mr-2" />
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {/* Tone selector */}
            <div className="flex flex-col gap-2">
              <Label htmlFor="tone">Tone</Label>
              <Select value={tone} onValueChange={(v) => setTone(v)}>
                <SelectTrigger id="tone" className="w-full">
                  <SelectValue placeholder="Select tone" />
                </SelectTrigger>
                <SelectContent>
                  {toneOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {/* Media URL */}
            <div className="flex flex-col gap-2 md:col-span-2">
              <Label htmlFor="mediaUrl">Media URL (optional)</Label>
              <Input
                id="mediaUrl"
                type="text"
                value={mediaUrl}
                onChange={(e) => setMediaUrl(e.target.value)}
                placeholder="https://..."
              />
            </div>
            {/* Content */}
            <div className="flex flex-col gap-2 md:col-span-2">
              <Label htmlFor="content">Post content</Label>
              <Textarea
                id="content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Write your post..."
                rows={4}
              />
            </div>
            {/* Schedule toggle */}
            <div className="flex items-center gap-2 md:col-span-2">
              <Switch
                id="schedule"
                checked={schedule}
                onCheckedChange={(checked) => setSchedule(checked)}
              />
              <Label htmlFor="schedule">Schedule for later</Label>
            </div>
            {/* Date picker - only show when schedule is enabled */}
            {schedule && (
              <div className="flex flex-col gap-2 md:col-span-2">
                <Label htmlFor="scheduledDate">
                  Select Date & Time ({getTimezoneName()}) - will be saved as UTC
                </Label>
                <Input
                  id="scheduledDate"
                  type="datetime-local"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  min={new Date().toISOString().slice(0, 16)}
                />
              </div>
            )}
            <div className="md:col-span-2 flex justify-end">
              <div className="flex flex-col w-full md:w-auto">
                {error && <div className="text-sm text-red-500 mb-2">{error}</div>}
                <Button type="submit" className="w-full md:w-auto" disabled={loading}>
                  {loading ? "Creating..." : "Create Post"}
                </Button>
              </div>
            </div>
          </form>
        </TabsContent>
        {/* Posts tab */}
        <TabsContent value="posts">
          {posts.length === 0 ? (
            <p className="text-sm text-muted-foreground">No posts yet. Create one in the Compose tab.</p>
          ) : (
            <ScrollArea className="h-96 pr-4">
              <div className="flex flex-col gap-4">
                {posts.map((post, idx) => (
                  <Card key={idx} className="shadow-sm border">
                    <CardHeader className="flex flex-row items-center gap-2">
                      {getPlatformIcon(post.platform)}
                      <div className="flex flex-col">
                        <span className="font-medium capitalize">
                          {post.platform}
                        </span>
                        <span className="text-xs capitalize text-muted-foreground">
                          Tone: {post.tone}
                        </span>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <p className="text-sm mb-2 whitespace-pre-line">
                        {post.content}
                      </p>
                      {post.mediaUrl && (
                        <a
                          href={post.mediaUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-500 underline"
                        >
                          View media
                        </a>
                      )}
                      <p className="text-xs mt-2 text-muted-foreground">
                        {post.schedule ? "Scheduled" : "Not scheduled"}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}