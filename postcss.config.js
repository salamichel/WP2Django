module.exports = {
  plugins: [
    require("@fullhuman/postcss-purgecss")({
      content: [
        "./templates/**/*.html",
        "./static/js/**/*.js",
        "./blog/**/*.py",
        "./contact/**/*.py",
      ],
      defaultExtractor: (content) => {
        // Capture standard HTML class names, including colons, slashes, dashes, and underscores
        return content.match(/[\w-/:]+(?<!:)/g) || [];
      },
      safelist: {
        standard: [
          /^is-/,
          /^has-/,
          /^active/,
          /^open/,
          /^show/,
          /^modal/,
          /^glightbox/,
          /^gdesc/,
          /^gslide/,
          /^goverlay/,
          /^gprev/,
          /^gnext/,
          /^gclose/,
          /^alert/,
          /^badge/,
          /^btn/,
          /^status/,
          /^pagination/,
          /^select2/,
          /^ck/,
          /^table/,
          /^swiper/,
        ],
        deep: [/ck-/, /select2/, /glightbox/, /admin/],
        greedy: [/is-/, /active/, /open/, /show/],
      },
    }),
    require("cssnano")({
      preset: [
        "default",
        {
          discardComments: { removeAll: true },
        },
      ],
    }),
  ],
};
