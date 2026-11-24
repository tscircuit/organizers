module.exports = {
  title: 'tscircuit organizers',
  tagline: 'Printable workshop organizers',
  url: 'https://organizers.tscircuit.com',
  baseUrl: '/',
  favicon: 'img/ts.svg',
  onBrokenLinks: 'throw',
  presets: [['classic', {
    docs: {routeBasePath: '/', sidebarPath: require.resolve('./sidebars.js'), breadcrumbs: false},
    blog: false,
    theme: {customCss: require.resolve('./src/css/custom.css')},
  }]],
  themeConfig: {
    navbar: {
      title: 'tscircuit organizers',
      logo: {alt: '', src: 'img/ts.svg'},
      items: [
        {to: '/', label: 'Organizers', position: 'left', activeBaseRegex: '^/$'},
        {href: 'https://docs.tscircuit.com', label: 'tscircuit docs', position: 'right'},
        {href: 'https://github.com/tscircuit/organizers', label: 'GitHub', position: 'right'},
      ],
    },
  },
};
