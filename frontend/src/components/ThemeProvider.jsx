import {createContext, useContext, useState}  from 'react';
import lightBg from '/herobg.jpeg';
import darkBg from '/liquid-bg.png';


export const ThemeContext = createContext();

 const ThemeProvider = ({children}) => {
    const [theme, setTheme] = useState('dark')
    const [bgImage, setBgImage] = useState(darkBg)

    const lightThemeToggle= () => {
        setTheme('light')
        setBgImage(lightBg)
    }
    const darkThemeToggle= () => {

        setTheme('dark')
        setBgImage(darkBg)
    }
    return (
        <ThemeContext.Provider value = {{theme, bgImage, lightThemeToggle, darkThemeToggle}}>
            {children}
        </ThemeContext.Provider>
    )
}

export default ThemeProvider;