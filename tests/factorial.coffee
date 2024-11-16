FUNCTION calcularFactorial(n)
	VAR factorial = 1;
	IF n < 0 THEN
        RETURN -1
	ELIF n == 0 THEN
		RETURN 1
	ELSE
		WHILE n > 1 THEN 
			factorial = factorial * n
			n = n - 1
		END
	END
	RETURN factorial
END

PRINT("Ingresa un numero entero")
VAR n = INPUT_INT()
VAR resultado = calcularFactorial(n)
IF resultado == -1 THEN 
    PRINT("El Factorial no esta definido para números negativos")
ELSE 
    PRINT("El factorial es: " + resultado)
END
