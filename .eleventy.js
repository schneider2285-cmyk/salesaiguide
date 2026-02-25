module.exports = function(eleventyConfig) {
  // Passthrough copy — everything that isn't .njk stays untouched
  // Directories
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("js");
  eleventyConfig.addPassthroughCopy("img");
  // compare/ and categories/ are now .njk templates — no passthrough needed
  eleventyConfig.addPassthroughCopy("guides/**/*.html");
  eleventyConfig.addPassthroughCopy("blog");
  eleventyConfig.addPassthroughCopy("editorial-policy");
  eleventyConfig.addPassthroughCopy("how-we-score");
  eleventyConfig.addPassthroughCopy("progress");
  // scripts/, docs/, coordination/, context/, _private/ are intentionally excluded — never published to live site

  // Root files
  eleventyConfig.addPassthroughCopy("_redirects");
  eleventyConfig.addPassthroughCopy("robots.txt");
  eleventyConfig.addPassthroughCopy("sitemap.xml");
  eleventyConfig.addPassthroughCopy("favicon.svg");

  // Root-level HTML files (about, 404, disclosure, editorial, logo-prototypes)
  // index.html is now generated from index.njk
  eleventyConfig.addPassthroughCopy("*.html");

  // Tool listing page (all reviews are now .njk templates)
  eleventyConfig.addPassthroughCopy("tools/index.html");

  return {
    dir: {
      input: ".",
      output: "_site",
      layouts: "_layouts",
      includes: "_includes",
      data: "_data"
    },
    templateFormats: ["njk"],
    htmlTemplateEngine: false
  };
};
