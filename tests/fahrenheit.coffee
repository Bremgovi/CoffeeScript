FUNCTION convertirAFahrenheit(celsius)
	RETURN (celsius*9/5) + 32
END

PRINT("Ingrese la temperatura en grados centigrados: ")
VAR celsius = INPUT()
VAR fahrenheit = convertirAFahrenheit(celsius)
PRINT(celsius + " grados celsius son equivalentes a " + fahrenheit + " fahrenheit")