// vue.config.js

function get_pages(page_names) {
  const pages = {};
  for (const page_name of page_names) {
    pages[page_name] = {
      entry: `src/pages/${page_name}.js`,
      filename: `html/${page_name}.html`,
    };
  }
  return pages;
}

/**
 * @type {import('@vue/cli-service').ProjectOptions}
 */
module.exports = {
  assetsDir: 'static/vue',
  pages: get_pages(['idol', 'event', 'gasha', 'card', 'events', 'gashas', 'idols', 'cards']),
}
