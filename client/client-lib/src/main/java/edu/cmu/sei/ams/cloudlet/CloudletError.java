package edu.cmu.sei.ams.cloudlet;

/**
 * User: jdroot
 * Date: 3/20/14
 * Time: 4:22 PM
 */
public class CloudletError extends Exception
{
    CloudletError(String message)
    {
        super(message);
    }

    CloudletError(String message, Throwable cause)
    {
        super(message, cause);
    }
}
