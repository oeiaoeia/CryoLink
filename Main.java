import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter purchase amount: ");
        double amount = sc.nextDouble();

        double discount = 0;

        if (amount < 1000)
            discount = 0;
        else if (amount < 5000)
            discount = amount * 0.05;
        else if (amount < 10000)
            discount = amount * 0.10;
        else if (amount < 20000)
            discount = amount * 0.15;
        else
            discount = amount * 0.20;

        System.out.println("Original Amount = ₹" + amount);
        System.out.println("Discount = ₹" + discount);
        System.out.println("Final Amount = ₹" + (amount - discount));
    }
}