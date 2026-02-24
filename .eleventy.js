module.exports = function(eleventyConfig) {
  // Passthrough copy — everything that isn't .njk stays untouched
  // Directories
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("js");
  eleventyConfig.addPassthroughCopy("img");
  eleventyConfig.addPassthroughCopy("compare");
  eleventyConfig.addPassthroughCopy("categories");
  eleventyConfig.addPassthroughCopy("guides");
  eleventyConfig.addPassthroughCopy("blog");
  eleventyConfig.addPassthroughCopy("editorial-policy");
  eleventyConfig.addPassthroughCopy("how-we-score");
  eleventyConfig.addPassthroughCopy("scripts");
  eleventyConfig.addPassthroughCopy("docs");
  eleventyConfig.addPassthroughCopy("coordination");
  eleventyConfig.addPassthroughCopy("context");

  // Root files
  eleventyConfig.addPassthroughCopy("_redirects");
  eleventyConfig.addPassthroughCopy("robots.txt");
  eleventyConfig.addPassthroughCopy("sitemap.xml");
  eleventyConfig.addPassthroughCopy("favicon.svg");

  // All root-level HTML files (index, about, 404, disclosure, editorial, logo-prototypes)
  eleventyConfig.addPassthroughCopy("*.html");

  // All tool review HTML files EXCEPT clay (which is now a .njk template)
  eleventyConfig.addPassthroughCopy("tools/*.html");

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
