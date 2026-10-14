# Java with the Maven wrapper, Spotless and Checkstyle. Gradle alternatives are in comments.
SETUP_CMD          = ./mvnw -q dependency:go-offline           # ./gradlew dependencies
FMT_CMD            = ./mvnw -q spotless:apply                  # ./gradlew spotlessApply
FMT_CHECK_CMD      = ./mvnw -q spotless:check                  # ./gradlew spotlessCheck
LINT_CMD           = ./mvnw -q checkstyle:check                # ./gradlew checkstyleMain
TYPECHECK_CMD      = ./mvnw -q compile test-compile            # ./gradlew compileJava compileTestJava
TEST_CMD           = ./mvnw -q verify                          # ./gradlew check
TEST_FAST_CMD      = ./mvnw -q test -DexcludedGroups=slow      # ./gradlew test -PexcludeTags=slow
BUILD_CMD          = ./mvnw -q package -DskipTests             # ./gradlew assemble
# Spotless formats the whole project; per-file formatting after each edit is skipped.
