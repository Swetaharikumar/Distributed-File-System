package test;

/** Configuration for running the test
 <p>
 This configuration file configures the command to start a naming server
 for naming test and several storage servers for storage test.

 NOTE: MUST have the same port number that follow port.config!!!
 We don't need to specify IP address here because it is all 'localhost' or '127.0.0.1'
 </p>
 */
public class Config {
    private static String separator = System.getProperty("path.separator", ":");

    /* Service port for your naming server and our test naming server */
    public static final int SERVICE_PORT = 8080;
    /* Registration port for your naming server and our test naming server */
    public static final int REGISTRATION_PORT = 8090;
    /* Storage ports for two storage servers. */
    public static final int[] STORAGE_PORTS = new int[] {7000, 7010};
    /* Command ports for two storage servers. */
    public static final int[] COMMAND_PORTS = new int[] {7001, 7011};

    /**
     * Command to start naming server.
     * TODO: change this string to start your own naming server.
     * Note: You must follow the specification in port.config!
     * After we run this command in the project's root directory, it should start a naming server
     * that listen on 2 ports: Config.SERVICE_PORT (for SERVICE) and CONFIG.REGISTRATION_PORT (for REGISTRATION).
    */
    public static final String startNaming = String.format("python3 naming/namingServer.py 8080 8090", separator);

    /**
     * Command to start the first storage server.
     * TODO: change this string to start your own storage server.
     * Note: You must follow the specification in port.config!
     * After we run this command in the project's root directory, it should start a storage server
     * that listen on 2 ports: Config.STORAGE_PORTS[0] (for CLIENT) and Config.COMMAND_PORTS[0] (for COMMAND).
     * It will also register it self through the naming server's REGISTRATION port Config.REGISTRATION_PORT.
     * This storage server will store all its files under the directory '/tmp/dist-systems-0'
    */
    public static final String startStorage0 = String.format("python3 storage/storage_server.py 7000 7001 8090 /tmp/storage0", separator);

    /**
     * Command to start the second storage server.
     * TODO: change this string to start your own storage server.
     * Note: You must follow the specification in port.config!
     * After we run this command in the project's root directory, it should start a storage server
     * that listen on 2 ports: Config.STORAGE_PORTS[1] (for CLIENT) and Config.COMMAND_PORTS[1] (for COMMAND).
     * It will also register it self through the naming server's REGISTRATION port Config.REGISTRATION_PORT.
     * This storage server will store all its files under the directory '/tmp/dist-systems-1'
    */
    public static final String startStorage1 = String.format("python3 storage/storage_server.py 7010 7011 8090 /tmp/storage1", separator);
}
