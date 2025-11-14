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
} from "lucide-react";
import { api } from "./lib/api";
import { getUser, isAuthenticated, clearAuth, type User } from "./lib/auth";
import Login from "./components/Login";

export default function SimpleMarketingDashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
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
  const [platformConnections, setPlatformConnections] = useState<Record<string, { connected: boolean; handle: string | null }>>({});
  const [checkingConnection, setCheckingConnection] = useState<boolean>(true);
  const [publishing, setPublishing] = useState<boolean>(false);
  const [disconnecting, setDisconnecting] = useState<Record<string, boolean>>({});

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

  // Map UI platform values to backend platform values
  const mapUiToBackendPlatform = (uiPlatform: string): string => {
    if (uiPlatform === "twitter") return "x";
    return uiPlatform;
  };

  // Map backend platform values to UI platform values
  const mapBackendToUiPlatform = (backendPlatform: string): string => {
    if (backendPlatform === "x") return "twitter";
    return backendPlatform;
  };

  const platformOptions = [
    { label: "Twitter", value: "twitter", icon: Twitter },
    { label: "Facebook", value: "facebook", icon: Facebook },
    { label: "Instagram", value: "instagram", icon: Instagram },
    { label: "LinkedIn", value: "linkedin", icon: Linkedin },
    { label: "YouTube", value: "youtube", icon: Youtube },
  ];

  const isPlatformConnected = (platform: string): boolean => {
    return platformConnections[platform]?.connected ?? false;
  };

  const checkAllPlatformConnections = async () => {
    if (!user) return; // Only check if user is authenticated
    setCheckingConnection(true);
    try {
      const res = await api.getAllPlatformStatus();
      if (res.ok) {
        const data = await res.json();
        // Convert backend platform keys to UI platform keys
        const uiConnections: Record<string, { connected: boolean; handle: string | null }> = {};
        for (const [backendPlatform, status] of Object.entries(data)) {
          const uiPlatform = mapBackendToUiPlatform(backendPlatform);
          uiConnections[uiPlatform] = status as { connected: boolean; handle: string | null };
        }
        setPlatformConnections(uiConnections);
      }
    } catch (err) {
      console.error("Failed to check platform connections:", err);
      // Silently fail - OAuth is optional
    } finally {
      setCheckingConnection(false);
    }
  };

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (isAuthenticated()) {
        const storedUser = getUser();
        if (storedUser) {
          setUser(storedUser);
          // Verify token is still valid
          try {
            const res = await api.getCurrentUser();
            if (res.ok) {
              const currentUser = await res.json();
              setUser(currentUser);
            } else {
              // Token invalid, clear auth
              clearAuth();
              setUser(null);
            }
          } catch {
            clearAuth();
            setUser(null);
          }
        }
      }
      setCheckingAuth(false);
    };
    checkAuth();
  }, []);

  // Check all platform connection statuses on mount and when user changes
  useEffect(() => {
    if (!user) return; // Only check if user is authenticated
    
    checkAllPlatformConnections();
    
    // Handle OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const oauthParam = urlParams.get("oauth");
    if (oauthParam === "success") {
      // Clear the URL parameter
      window.history.replaceState({}, document.title, window.location.pathname);
      // Check connection status again
      setTimeout(() => checkAllPlatformConnections(), 1000);
    }
  }, [user]);

  // Update platform selection if current platform becomes disconnected
  useEffect(() => {
    if (!user) return; // Only run if user is authenticated
    if (!checkingConnection && !isPlatformConnected(platform)) {
      // Find first connected platform
      const firstConnected = platformOptions.find(opt => isPlatformConnected(opt.value));
      if (firstConnected) {
        setPlatform(firstConnected.value);
      }
    }
  }, [platformConnections, checkingConnection, platform, user]);

  const handleLoginSuccess = (loggedInUser: User) => {
    setUser(loggedInUser);
  };

  const handleLogout = () => {
    api.logout();
    clearAuth();
    setUser(null);
  };

  // Show login if not authenticated
  if (checkingAuth) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div>Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const toneOptions = [
    { label: "Professional", value: "professional" },
    { label: "Casual", value: "casual" },
    { label: "Playful", value: "playful" },
    { label: "Inspirational", value: "inspirational" },
  ];

  const getPlatformHandle = (platform: string): string | null => {
    return platformConnections[platform]?.handle ?? null;
  };

  const handlePlatformConnect = (platform: string) => {
    const backendPlatform = mapUiToBackendPlatform(platform);
    api.authorizePlatform(backendPlatform);
  };

  const handlePlatformDisconnect = async (platform: string) => {
    const backendPlatform = mapUiToBackendPlatform(platform);
    setDisconnecting(prev => ({ ...prev, [platform]: true }));
    try {
      const res = await api.disconnectPlatform(backendPlatform);
      if (res.ok) {
        // Refresh connection status
        await checkAllPlatformConnections();
      } else {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
    } catch (err: any) {
      console.error(`Failed to disconnect ${platform}:`, err);
      alert(err?.message || `Failed to disconnect from ${platform}`);
    } finally {
      setDisconnecting(prev => ({ ...prev, [platform]: false }));
    }
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
        <div>
          <h1 className="text-2xl font-bold">Marketing Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Logged in as {user.email}
          </p>
        </div>
        <div className="flex items-center gap-4">
          {/* Platform Connections */}
          <div className="flex items-center gap-2 flex-wrap">
            {checkingConnection ? (
              <span className="text-sm text-muted-foreground">Checking connections...</span>
            ) : (
              platformOptions.map((opt) => {
                const connected = isPlatformConnected(opt.value);
                const handle = getPlatformHandle(opt.value);
                const Icon = opt.icon;
                const isDisconnecting = disconnecting[opt.value] || false;
                
                return (
                  <div key={opt.value} className="flex items-center gap-2">
                    {connected ? (
                      <Button
                        onClick={() => handlePlatformDisconnect(opt.value)}
                        variant="outline"
                        size="sm"
                        disabled={isDisconnecting}
                        className="flex items-center gap-2 text-green-600 border-green-600 hover:bg-green-50"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        {isDisconnecting ? "Disconnecting..." : `Connected${handle ? `: @${handle}` : ""}`}
                      </Button>
                    ) : (
                      <Button
                        onClick={() => handlePlatformConnect(opt.value)}
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-2"
                      >
                        <Icon className="w-4 h-4" />
                        Connect {opt.label}
                      </Button>
                    )}
                  </div>
                );
              })
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
          {/* Logout Button */}
          <Button
            onClick={handleLogout}
            variant="outline"
            size="sm"
          >
            Logout
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
                  {platformOptions.map((opt) => {
                    const connected = isPlatformConnected(opt.value);
                    return (
                      <SelectItem 
                        key={opt.value} 
                        value={opt.value} 
                        className="flex items-center"
                        disabled={!connected}
                      >
                        <opt.icon className="w-4 h-4 mr-2" />
                        {opt.label} {connected ? "" : "(Not Connected)"}
                      </SelectItem>
                    );
                  })}
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