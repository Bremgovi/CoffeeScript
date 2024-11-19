FUNCTION esPrimo(x)
    IF x <= 1 THEN RETURN FALSE
    VAR i = 2
    WHILE i <= x / 2 THEN
        IF x % i == 0 THEN
            RETURN FALSE
        END
        i = i + 1
    END
    RETURN TRUE
END

PRINT("Ingresa un numero entero")
VAR n = INPUT()
IF esPrimo(n) THEN
    PRINT(n + " es un numero primo")
ELSE
    PRINT(n + " NO es un numero primo")
END