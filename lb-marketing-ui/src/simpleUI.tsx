import React, { useState } from "react";
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
} from "lucide-react";

/**
 * A simple marketing dashboard UI for creating and viewing social media posts.
 *
 * This component provides two main sections:
 *  1. Compose – a form where users can draft a new post. It allows selection
 *     of a target platform, tone, an optional media URL, and the post content.
 *     A schedule toggle lets users choose to schedule immediately or not.
 *  2. Posts – displays a scrollable list of posts that have been created
 *     in this session. Each post card shows the platform, tone, content and
 *     whether or not the post was scheduled.
 *
 * Note: In a production application you would likely persist posts to a backend
 * service. For this simple UI they live only in local state.
 */
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
  const [posts, setPosts] = useState<Post[]>([]);

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    const newPost: Post = {
      platform,
      tone,
      mediaUrl: mediaUrl.trim(),
      content: content.trim(),
      schedule,
    };
    setPosts([newPost, ...posts]);
    // reset form
    setContent("");
    setMediaUrl("");
    setSchedule(false);
  };

  const getPlatformIcon = (platformKey: string) => {
    const found = platformOptions.find((p) => p.value === platformKey);
    return found ? <found.icon className="w-4 h-4 mr-2" /> : null;
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      <h1 className="text-2xl font-bold">Marketing Dashboard</h1>
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
              <Label htmlFor="schedule">Schedule immediately</Label>
            </div>
            <div className="md:col-span-2 flex justify-end">
              <Button type="submit" className="w-full md:w-auto">
                Create Post
              </Button>
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
                        {post.schedule ? "Scheduled immediately" : "Not scheduled"}
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