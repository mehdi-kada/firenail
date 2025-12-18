import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
    return {
        rules: [
            {
                userAgent: "*",
                allow: "/",
                disallow: ["/auth/", "/generate", "/thumbnails", "/api/"],
            },
        ],
        sitemap: "https://firenail.ai/sitemap.xml",
    };
}
