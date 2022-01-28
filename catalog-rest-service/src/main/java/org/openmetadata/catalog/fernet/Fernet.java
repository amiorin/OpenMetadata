/*
 *  Copyright 2021 Collate
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  http://www.apache.org/licenses/LICENSE-2.0
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

package org.openmetadata.catalog.fernet;

import static org.openmetadata.catalog.exception.CatalogExceptionMessage.*;

import com.google.common.annotations.VisibleForTesting;
import com.macasaet.fernet.Key;
import com.macasaet.fernet.StringValidator;
import com.macasaet.fernet.Token;
import com.macasaet.fernet.Validator;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.TemporalAmount;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import lombok.NonNull;
import org.openmetadata.catalog.CatalogApplicationConfig;

public class Fernet {
  private static Fernet instance;
  private String fernetKey;
  public static String FERNET_PREFIX = "fernet:";
  private Validator<String> validator;

  private Fernet() {
    this.validator =
        new StringValidator() {
          public TemporalAmount getTimeToLive() {
            return Duration.ofSeconds(Instant.MAX.getEpochSecond());
          }
        };
  }

  public static Fernet getInstance() {
    if (instance == null) {
      instance = new Fernet();
    }
    return instance;
  }

  public void initialize(CatalogApplicationConfig config) {
    FernetConfiguration fernetConfiguration = config.getFernetConfiguration();
    String fernetKey = fernetConfiguration != null ? fernetConfiguration.getFernetKey() : null;
    setFernetKey(fernetKey);
  }

  @VisibleForTesting
  public Fernet(String fernetKey) {
    this();
    this.setFernetKey(fernetKey);
  }

  @VisibleForTesting
  public void setFernetKey(String fernetKey) {
    this.fernetKey = fernetKey;
  }

  public Boolean isKeyDefined() {
    return fernetKey != null;
  }

  public String encrypt(@NonNull String secret) {
    if (secret.startsWith(FERNET_PREFIX)) {
      throw new IllegalArgumentException(isAlreadyTokenized());
    }
    if (fernetKey != null) {
      Key key = new Key(fernetKey.split(",")[0]);
      return FERNET_PREFIX + Token.generate(key, secret).serialise();
    }
    throw new IllegalArgumentException(fernetKeyNotDefined());
  }

  public static Boolean isTokenized(String tokenized) {
    return tokenized.startsWith(FERNET_PREFIX);
  }

  public String decrypt(String tokenized) {
    if (fernetKey == null) {
      throw new IllegalArgumentException(fernetKeyNotDefined());
    }
    if (tokenized != null && tokenized.startsWith(FERNET_PREFIX)) {
      String str = tokenized.split(FERNET_PREFIX, 2)[1];
      Token token = Token.fromString(str);
      List<Key> keys = Arrays.stream(fernetKey.split(",")).map(Key::new).collect(Collectors.toList());
      return token.validateAndDecrypt(keys, validator);
    }
    throw new IllegalArgumentException(isNotTokenized());
  }
}
