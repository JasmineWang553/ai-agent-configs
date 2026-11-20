# Maven Builds Behind Charter Artifactory

Before running `mvn` on a project that uses `artifactory.se-charter.net`
(fixes `SunCertPathBuilderException`):

1. **Pick the JDK from the pom.** Check `pom.xml` for the Java version
   (`java.version` / `maven.compiler.release` / `<release>`), then set
   `JAVA_HOME` to the matching JDK:
   - Java 21 → `export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home`
   - Java 25 → `export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-25.jdk/Contents/Home`

2. **Add the Charter cert to a per-JDK local trust store (no sudo)**, then build:

```bash
host="artifactory.se-charter.net"
jdk_key=$(echo "$JAVA_HOME" | sed 's#[/ ]#_#g')
localcacerts="/tmp/charter-ssl/$jdk_key/cacerts"
mkdir -p "$(dirname "$localcacerts")"
[ -f "$localcacerts" ] || { cp "$JAVA_HOME/lib/security/cacerts" "$localcacerts"; chmod u+w "$localcacerts"; }
if ! "$JAVA_HOME/bin/keytool" -list -alias secharter -keystore "$localcacerts" -storepass changeit >/dev/null 2>&1; then
  certfile=$(mktemp /tmp/secharter-XXXX.crt)
  openssl s_client -connect "${host}:443" </dev/null 2>/dev/null \
    | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > "$certfile"
  "$JAVA_HOME/bin/keytool" -importcert -alias secharter -keystore "$localcacerts" \
    -file "$certfile" -storepass changeit -noprompt
  rm -f "$certfile"
fi
mvn -Djavax.net.ssl.trustStore="$localcacerts" -Djavax.net.ssl.trustStorePassword=changeit clean install
```
