#pragma once

#include <boost/asio.hpp>
#include <boost/beast.hpp>
#include <queue>
#include <string>

namespace net  = boost::asio;
namespace beast = boost::beast;
namespace websocket = beast::websocket;
using tcp = net::ip::tcp;

class WebSocketClient : public std::enable_shared_from_this<WebSocketClient> {
public:
    explicit WebSocketClient(net::io_context& ioc)
        : resolver_(ioc), ws_(ioc), strand_(net::make_strand(ioc)) {}

    // Block until fully connected
    void connect(const std::string& host, const std::string& port) {
        auto results = resolver_.resolve(host, port);
        auto ep = net::connect(ws_.next_layer(), results);
        host_ = host + ":" + std::to_string(ep.port());

        // Do the handshake (blocking)
        ws_.handshake(host_, "/");
    }

    // Queue a message to be sent asynchronously
    void async_send(const std::string& message) {
        net::post(strand_,
            [self = shared_from_this(), message]() {
                bool writing_in_progress = !self->write_queue_.empty();
                self->write_queue_.push(message);
                if (!writing_in_progress) {
                    self->do_write();
                }
            });
    }

private:
    void do_write() {
        ws_.async_write(
            net::buffer(write_queue_.front()),
            net::bind_executor(
                strand_,
                [self = shared_from_this()](beast::error_code ec, std::size_t) {
                    if (!ec) {
                        self->write_queue_.pop();
                        if (!self->write_queue_.empty()) {
                            self->do_write();
                        }
                    } else {
                        // TODO: handle error
                    }
                }));
    }

    tcp::resolver resolver_;
    websocket::stream<tcp::socket> ws_;
    net::strand<net::io_context::executor_type> strand_;

    std::queue<std::string> write_queue_;
    std::string host_;
};
