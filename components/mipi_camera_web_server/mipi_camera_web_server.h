#pragma once

#include "esphome/core/component.h"
#include "esphome/components/mipi_dsi_cam/mipi_dsi_cam.h"

#ifdef USE_ESP32_VARIANT_ESP32P4
#include <esp_http_server.h>
#include <esp_timer.h>
#include <freertos/semphr.h>
#include <vector>
#endif

namespace esphome {
namespace mipi_camera_web_server {

class MipiCameraWebServer : public Component {
 public:
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::WIFI - 1.0f; }

  // Configuration depuis __init__.py
  void set_camera(mipi_dsi_cam::MipiDsiCam *camera) { this->camera_ = camera; }
  void set_port(uint16_t port) { this->port_ = port; }

  void enable_jpeg_stream(bool enable) { this->enable_jpeg_ = enable; }
  void enable_h264_stream(bool enable) { this->enable_h264_ = enable; }

 protected:
  mipi_dsi_cam::MipiDsiCam *camera_{nullptr};
  uint16_t port_{80};

#ifdef USE_ESP32_VARIANT_ESP32P4
  httpd_handle_t server_{nullptr};

  // Buffers PSRAM
  uint8_t *jpeg_buffer_{nullptr};
  size_t jpeg_buffer_size_{150 * 1024};
  SemaphoreHandle_t frame_mutex_{nullptr};

  // État
  bool enable_jpeg_{true};
  bool enable_h264_{false};
  bool streaming_active_{false};

  // === Handlers HTTP ===
  static esp_err_t index_handler_(httpd_req_t *req);
  static esp_err_t stream_jpeg_handler_(httpd_req_t *req);
  static esp_err_t stream_h264_handler_(httpd_req_t *req);
  static esp_err_t snapshot_handler_(httpd_req_t *req);
  static esp_err_t control_handler_(httpd_req_t *req);

  // === Utilitaires ===
  bool encode_jpeg_(const uint8_t *rgb565_data, size_t width, size_t height,
                    uint8_t **jpeg_out, size_t *jpeg_size, int quality = 12);
  bool encode_h264_(const uint8_t *rgb_data, size_t width, size_t height,
                    std::vector<uint8_t> &out_stream);
  static void rgb565_to_rgb888_(const uint8_t *rgb565, uint8_t *rgb888, size_t pixels);

  // === Initialisation serveur ===
  bool start_web_server_();
  void stop_web_server_();

#endif  // USE_ESP32_VARIANT_ESP32P4
};

}  // namespace mipi_camera_web_server
}  // namespace esphome

