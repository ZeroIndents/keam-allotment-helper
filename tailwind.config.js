/** @type {import('tailwindcss').Config} */
// REBUILD AFTER CHANGING CLASSES IN statistics.html:
//   npx tailwindcss -c tailwind.config.js -i static/tailwind.input.css -o static/tailwind.css --minify
module.exports = {
  darkMode: 'class',
  // statistics.html is the only template that uses Tailwind.
  content: ['./templates/statistics.html'],
  theme: { extend: {} },
  plugins: [],
};
