/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './django_dash/templates/**/*.html',   // Scan HTML templates for Tailwind classes
        './django_dash/static/**/*.js',        // Include all JavaScript files in static directory
        './django_dash/static/admin/css/styles.css',  // Admin-specific CSS
        './django_dash/**/*.py',              // Include Python files for possible Jinja-style Tailwind classes
        './django_dash/static/**/*.jsx',       // Include JSX files
    ],

    theme: {
        extend: {
            fontFamily: {
                vazir: ['Vazir', 'sans-serif'],   // Define the Vazir font
                roboto: ['Cantarell', 'sans-serif'], // Define the Roboto font
            },
            animation: {
                'bounce-once': 'bounce 1s ease-in-out 1',
                'heartbeat': 'heartbeat 1.5s ease-in-out infinite',
            },
            keyframes: {
                'heartbeat': {
                    '0%, 100%': {transform: 'scale(1)'},
                    '50%': {transform: 'scale(1.2)'},
                },
            },
        },
    },

    daisyui: {
        themes: [
            "light",
            "dark",
            "dracula",
            "dim",
            "autumn",
            "lemonade",
        ],  // Include themes from DaisyUI
    },

    plugins: [
        require('daisyui'),  // DaisyUI for additional UI components
    ],
}